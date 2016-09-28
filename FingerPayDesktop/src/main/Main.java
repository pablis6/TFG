package main;

import entity.Persona;
import view.Principal;

public class Main {

	public static void main(String[] args) {
		new Principal(new Persona()).setVisible(true);
	}

}
