package Controller;

import Model.Model;

import com.digitalpersona.onetouch.DPFPSample;

public class Controller {

	private Model model;
	
	public Controller() {
		model = new Model();
	}

	public boolean ProcesarCaptura(DPFPSample muestra, String id_terminal){
		return model.ProcesarCaptura(muestra, id_terminal);
	}

	public void generaTxt(String id_terminal, String pin, String money) {
		model.generaTxt(id_terminal, pin, money);
	}

	public String monitorizar() {
		return model.monitorizar();
	}
}
