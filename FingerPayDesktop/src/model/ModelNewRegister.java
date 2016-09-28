package model;

import java.awt.Image;
import java.awt.image.RenderedImage;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

import javax.imageio.ImageIO;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.digitalpersona.onetouch.DPFPGlobal;
import com.digitalpersona.onetouch.DPFPSample;

import entity.Persona;

public class ModelNewRegister {
	private Logger logger;
	private final String REGISTER = "REGISTER";

	public ModelNewRegister() {
		//Logger
		logger = LoggerFactory.getLogger(ModelNewRegister.class); 
		
	}

	public boolean comprobar(Persona persona) {
		return false;
	}

	public Image ProcesarCaptura(DPFPSample muestra, String id_terminal){
		
		if(muestra != null){
  	    	Image image = DPFPGlobal.getSampleConversionFactory().createImage(muestra);
	        logger.info("Guardando imagen...");
  	    	try {
  				ImageIO.write((RenderedImage) image, "jpg", new File("huellas/"+ id_terminal + ".jpg"));
  				
  			} catch (IOException e) {
  				logger.error("Ha ocurrido un fallo y no se ha podido guardar la imagen");
  				return null;
  			}
  	    	return image;
		}
		return null;
	}

	public void generaTxt(Persona persona, String id_terminal) {
		String ruta = "huellas/"+ id_terminal + ".txt";
        
        try {
        	FileWriter archivo = new FileWriter(ruta);
            BufferedWriter bw = new BufferedWriter(archivo);
			
			bw.write(id_terminal + '\n');
			bw.write(REGISTER + '\n');
			bw.write(persona.getPin() + '\n');
			bw.write(persona.getNombre() + '\n');
			bw.write(persona.getApellido1() + '\n');
			bw.write(persona.getApellido2() + '\n');
			bw.write(persona.getDni() + '\n');
			bw.write(persona.getEmail() + '\n');
			bw.write(persona.getTelefono() + '\n');
			
			
	        bw.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			logger.error(e.getMessage());
		}
		
	}

	
}
