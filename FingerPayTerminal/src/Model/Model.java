package Model;

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

import javax.imageio.ImageIO;

import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.digitalpersona.onetouch.DPFPGlobal;
import com.digitalpersona.onetouch.DPFPSample;

public class Model {
	private Logger logger;
	private final String CHARGE = "CHARGE";
	
	public Model() {
		//Logger
		logger = LoggerFactory.getLogger(Model.class); 
	}

	public boolean ProcesarCaptura(DPFPSample muestra, String id_terminal){
		
		if(muestra != null){
  	    	Image image = DPFPGlobal.getSampleConversionFactory().createImage(muestra);
	        //EnviarTexto("La plantilla de huella ha sido creada. Puede Verificar o Identificarla");
	        //guardar
  	    	try {
  				ImageIO.write((RenderedImage) image, "jpg", new File("huellas/"+ id_terminal + ".jpg"));
  				
  			} catch (IOException e) {
  				//logger
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
			bw.write(new String(pin) + '\n');
			bw.write(money + '\n');
			
	        bw.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			logger.error(e.getMessage());
		}
	}

	@SuppressWarnings({ "null", "rawtypes" })
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
			WatchKey key = watchService.take();
			// Algo ocurrio en el directorio para los eventos registrados
			while (key != null) {
               for (WatchEvent event : key.pollEvents()) {
            	   String eventKind = event.kind().toString();
                   String file = event.context().toString();
                   valoracion = valoraMensaje(StringUtils.join(directory, "/", file));
                   key = null;
               }
			}
			watchService.close();
			logger.info("finaliza la monitorizacion");
			
		} catch (IOException | InterruptedException e) {
			logger.error(e.getMessage());
		}
		return valoracion;
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
