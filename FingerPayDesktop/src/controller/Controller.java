package controller;

import java.awt.Image;

import model.ModelNewRegister;

import com.digitalpersona.onetouch.DPFPSample;

import entity.Persona;

public class Controller {

	private ModelNewRegister modeloRegistro;
	
	public Controller() {
		modeloRegistro = new ModelNewRegister();
	}

	public boolean comprobar(Persona persona) {
		return modeloRegistro.comprobar(persona);
	}

	public Image ProcesarCaptura(DPFPSample sample, String iD_TERMINAL) {
		return modeloRegistro.ProcesarCaptura(sample, iD_TERMINAL);
	}

	public void generaTxt(Persona persona, String id_terminal) {
		modeloRegistro.generaTxt(persona, id_terminal);
		
	}

}
