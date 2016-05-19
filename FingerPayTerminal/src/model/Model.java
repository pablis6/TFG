package model;

import static java.nio.file.StandardWatchEventKinds.ENTRY_CREATE;

import java.awt.Image;
import java.awt.image.RenderedImage;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.WatchEvent;
import java.nio.file.WatchKey;
import java.nio.file.WatchService;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;

import javax.imageio.ImageIO;

import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.digitalpersona.onetouch.DPFPGlobal;
import com.digitalpersona.onetouch.DPFPSample;

public class Model {
	private Logger logger;
	private final String CHARGE = "CHARGE";
	private boolean terminado;
	
	public Model() {
		//Logger
		logger = LoggerFactory.getLogger(Model.class);
		terminado = false;
	}

	public boolean ProcesarCaptura(DPFPSample muestra, String id_terminal){
		
		if(muestra != null){
  	    	Image image = DPFPGlobal.getSampleConversionFactory().createImage(muestra);
	        logger.info("Guardando imagen...");
  	    	try {
  				ImageIO.write((RenderedImage) image, "jpg", new File("huelas/"+ id_terminal + ".jpg"));
  				
  			} catch (Exception e) {
  				logger.error("Ha ocurrido un fallo y no se ha podido guardar la imagen");
  				return false;
  			}
  	    	return true;
		}
		return false;
	}

	public void generaTxt(String id_terminal, String pin, String money) {
		String ruta = "huellas/"+ id_terminal + ".txt";
        
        try {
        	FileWriter archivo = new FileWriter(ruta);
            BufferedWriter bw = new BufferedWriter(archivo);
			
			bw.write(id_terminal + '\n');
			bw.write(CHARGE + '\n');
			bw.write(pin + '\n');
			bw.write(money + '\n');
			
	        bw.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			logger.error(e.getMessage());
		}
	}

	
	@SuppressWarnings("rawtypes")
	public String monitorizar() {
		String valoracion = "";
		try {
			String directory = "respuestas";
			logger.info("monitorizando la carpeta: " + directory);
			// Obtenemos el directorio
			Path directoryToWatch = Paths.get(directory);
			// Solicitamos el servicio WatchService
			WatchService watchService = directoryToWatch.getFileSystem().newWatchService();
			// Registramos los eventos que queremos monitorear
			directoryToWatch.register(watchService, new WatchEvent.Kind[] {ENTRY_CREATE});
			
			logger.info("comienza la monitorizacion");
			// Esperamos que algo suceda con el directorio
			
			WatchKey key = watchService.poll(60, TimeUnit.SECONDS);

			while (key != null) {
               for (WatchEvent event : key.pollEvents()) {
                   String file = event.context().toString();
                   valoracion = valoraMensaje(StringUtils.join(directory, "/", file));
                   key = null; //key.reset();
                   terminado = true;
               }
			}

			if(!terminado){
				generaTimeOutTxt();
				WatchKey key2 = watchService.take();
				
				
				for (WatchEvent event : key2.pollEvents()) {
                   String file = event.context().toString();
                   valoracion = valoraMensaje(StringUtils.join(directory, "/", file));
               }
			}
			
			watchService.close();
			logger.info("finaliza la monitorizacion");
			
			terminado = false;
			
		} catch (IOException | InterruptedException e) {
			logger.error(e.getMessage());
		}
		return valoracion;
	}
	
	private void generaTimeOutTxt(){
		String ruta = "respuestas/"+ "timeout" + ".txt";
        
        try {
        	FileWriter archivo = new FileWriter(ruta);
            BufferedWriter bw = new BufferedWriter(archivo);
			
			bw.write("TIMEOUT" + '\n');
			bw.write("El servidor tarda demasiado en contestar" + '\n');
			
	        bw.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			logger.error(e.getMessage());
		}
	}
	
	private String valoraMensaje(String archivo) throws IOException{
		logger.info("comienza la valoracion del mensaje");
		String ret;
		String line;
		List<String> txt = new ArrayList<String>();
		FileReader file = new FileReader(archivo);
		BufferedReader br = new BufferedReader(file);
		while((line = br.readLine())!=null) {
	        txt.add(line);
		}
		ret = StringUtils.join(txt, "|");
		br.close();
		logger.info("finaliza la valoracion del mensaje");
		
		logger.info("comienza el borrado del archivo");
		File f = new File(archivo);
		if(f.delete()){
			logger.info("borrado correctamente");
		}
		else {
			logger.info("fallo en el borrado del archivo");
		}
		
		
		return ret;
	}
}
