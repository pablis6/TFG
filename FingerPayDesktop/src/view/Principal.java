package view;

import java.awt.Component;
import java.awt.Font;
import java.awt.Insets;
import java.awt.Rectangle;
import java.awt.Toolkit;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;

import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JTabbedPane;
import javax.swing.JTextField;
import javax.swing.SwingConstants;

import org.eclipse.wb.swing.FocusTraversalOnArray;

import controller.Controller;
import entity.Persona;
import javax.swing.border.LineBorder;
import java.awt.Color;

public class Principal extends JFrame{
	private JTabbedPane tpOpciones;
	private JTextField tfDNI, tfNombre, tfApellido1, tfApellido2, tfEmail, tfTelefono;
	private JLabel lblDNI, lblNombre, lblApellido1, lblApellido2, lblEmail, lblTelefono;
	private JPanel panelRegistro;
	private JButton btnLimpiar, btnSiguiente;
	
	private Controller control;
		
	public Principal(Persona p){
		setIconImage(Toolkit.getDefaultToolkit().createImage(this.getClass().getClassLoader().getResource("images/fingerPay.png")));
		setResizable(false);
		setTitle("FingerPay");
		
		control = new Controller();
		
		setBounds(new Rectangle(300, 200, 750, 400));
		getContentPane().setLayout(null);
		
//		tpOpciones = new JTabbedPane(JTabbedPane.TOP);
//		tpOpciones.setBounds(10, 11, 714, 340);
//		getContentPane().add(tpOpciones);
		
		panelRegistro = new JPanel();
		panelRegistro.setBorder(new LineBorder(new Color(0, 0, 0), 1, true));
		//tpOpciones.addTab("Nuevo registro", null, panelRegistro, null);
		panelRegistro.setLayout(null);
		panelRegistro.setBounds(10, 11, 714, 341);
		getContentPane().add(panelRegistro);
		
		lblNombre = new JLabel("Nombre:");
		lblNombre.setFont(new Font("Tahoma", Font.PLAIN, 18));
		lblNombre.setHorizontalAlignment(SwingConstants.RIGHT);
		lblNombre.setBounds(10, 30, 150, 40);
		panelRegistro.add(lblNombre);
		
		tfNombre = new JTextField();
		tfNombre.setFont(new Font("Tahoma", Font.PLAIN, 18));
		tfNombre.setToolTipText("");
		tfNombre.setBounds(170, 30, 215, 40);
		panelRegistro.add(tfNombre);
		tfNombre.setColumns(10);
		tfNombre.requestFocusInWindow();
		tfNombre.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				tfApellido1.requestFocusInWindow();
			}
		});
		
		lblApellido1 = new JLabel("Primer apellido:");
		lblApellido1.setFont(new Font("Tahoma", Font.PLAIN, 18));
		lblApellido1.setHorizontalAlignment(SwingConstants.RIGHT);
		lblApellido1.setBounds(10, 100, 150, 40);
		panelRegistro.add(lblApellido1);
		
		tfApellido1 = new JTextField();
		tfApellido1.setFont(new Font("Tahoma", Font.PLAIN, 18));
		tfApellido1.setBounds(170, 100, 215, 40);
		panelRegistro.add(tfApellido1);
		tfApellido1.setColumns(10);
		tfApellido1.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				tfApellido2.requestFocusInWindow();
			}
		});
		
		lblApellido2 = new JLabel("Segundo apellido:");
		lblApellido2.setFont(new Font("Tahoma", Font.PLAIN, 18));
		lblApellido2.setHorizontalAlignment(SwingConstants.RIGHT);
		lblApellido2.setBounds(10, 170, 150, 40);
		panelRegistro.add(lblApellido2);
		
		tfApellido2 = new JTextField();
		tfApellido2.setFont(new Font("Tahoma", Font.PLAIN, 18));
		tfApellido2.setColumns(10);
		tfApellido2.setBounds(170, 170, 215, 40);
		panelRegistro.add(tfApellido2);
		tfApellido2.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				tfDNI.requestFocusInWindow();
			}
		});
		
		lblDNI = new JLabel("DNI:");
		lblDNI.setFont(new Font("Tahoma", Font.PLAIN, 18));
		lblDNI.setHorizontalAlignment(SwingConstants.RIGHT);
		lblDNI.setBounds(395, 30, 75, 40);
		panelRegistro.add(lblDNI);
		
		tfDNI = new JTextField();
		tfDNI.setFont(new Font("Tahoma", Font.PLAIN, 18));
		tfDNI.setBounds(480, 30, 215, 40);
		panelRegistro.add(tfDNI);
		tfDNI.setColumns(10);
		tfDNI.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				tfEmail.requestFocusInWindow();
			}
		});
		
		lblEmail = new JLabel("Email:");
		lblEmail.setFont(new Font("Tahoma", Font.PLAIN, 18));
		lblEmail.setHorizontalAlignment(SwingConstants.RIGHT);
		lblEmail.setBounds(395, 100, 75, 40);
		panelRegistro.add(lblEmail);
		
		tfEmail = new JTextField();
		tfEmail.setFont(new Font("Tahoma", Font.PLAIN, 18));
		tfEmail.setBounds(480, 100, 215, 40);
		panelRegistro.add(tfEmail);
		tfEmail.setColumns(10);
		tfEmail.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				tfTelefono.requestFocusInWindow();
			}
		});
		
		lblTelefono = new JLabel("Telefono:");
		lblTelefono.setFont(new Font("Tahoma", Font.PLAIN, 18));
		lblTelefono.setHorizontalAlignment(SwingConstants.RIGHT);
		lblTelefono.setBounds(395, 170, 75, 40);
		panelRegistro.add(lblTelefono);
		
		tfTelefono = new JTextField();
		tfTelefono.setToolTipText("");
		tfTelefono.setFont(new Font("Tahoma", Font.PLAIN, 18));
		tfTelefono.setBounds(480, 170, 215, 40);
		panelRegistro.add(tfTelefono);
		tfTelefono.setColumns(10);
		tfTelefono.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				btnSiguiente.requestFocusInWindow();
			}
		});
		tfTelefono.addKeyListener(new KeyAdapter() {
			@Override
			public void keyTyped(KeyEvent arg0) {
				@SuppressWarnings("unused")
				int key = arg0.getKeyChar();
	            //solo numeros
	            if (key < 48 || key > 57){
	            	arg0.consume();
	            }
			}
		});
		
		btnLimpiar = new JButton(new ImageIcon(getClass().getResource("/images/clear.png")));
		btnLimpiar.setVerticalTextPosition(SwingConstants.BOTTOM);
		btnLimpiar.setHorizontalTextPosition(SwingConstants.CENTER);
		btnLimpiar.setMargin(new Insets(0, 0, 0, 0));
		btnLimpiar.setToolTipText("Limpia los campos escritos");
		btnLimpiar.setBounds(10, 239, 90, 90);
		panelRegistro.add(btnLimpiar);
		btnLimpiar.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				Limpiar();
			}
		});
		
		
		btnSiguiente = new JButton(new ImageIcon(getClass().getResource("/images/next.png")));
		btnSiguiente.setVerticalTextPosition(SwingConstants.BOTTOM);
		btnSiguiente.setHorizontalTextPosition(SwingConstants.CENTER);
		btnSiguiente.setMargin(new Insets(0, 0, 0, 0));
		btnSiguiente.setToolTipText("Siguiente paso");
		btnSiguiente.setBounds(614, 239, 90, 90);
		panelRegistro.add(btnSiguiente);
		btnSiguiente.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				Comprobar();
			}
		});
		
		
		tfNombre.setText(p.getNombre());
		tfApellido1.setText(p.getApellido1());
		tfApellido2.setText(p.getApellido2());
		tfDNI.setText(p.getDni());
		tfEmail.setText(p.getEmail());
		
		JLabel lblObligatorio1 = new JLabel("*");
		lblObligatorio1.setForeground(Color.RED);
		lblObligatorio1.setBounds(160, 30, 15, 14);
		panelRegistro.add(lblObligatorio1);
		
		JLabel lblObligatorio2 = new JLabel("*");
		lblObligatorio2.setForeground(Color.RED);
		lblObligatorio2.setBounds(160, 100, 15, 14);
		panelRegistro.add(lblObligatorio2);
		
		JLabel lblObligatorio3 = new JLabel("*");
		lblObligatorio3.setForeground(Color.RED);
		lblObligatorio3.setBounds(160, 170, 15, 14);
		panelRegistro.add(lblObligatorio3);
		
		JLabel lblObligatorio4 = new JLabel("*");
		lblObligatorio4.setForeground(Color.RED);
		lblObligatorio4.setBounds(470, 30, 15, 14);
		panelRegistro.add(lblObligatorio4);
		
		JLabel lblObligatorio5 = new JLabel("*");
		lblObligatorio5.setForeground(Color.RED);
		lblObligatorio5.setBounds(470, 100, 15, 14);
		panelRegistro.add(lblObligatorio5);
		
		if(p.getTelefono() != "0"){
			tfTelefono.setText(p.getTelefono());
		}
		
		
		panelRegistro.setFocusTraversalPolicy(new FocusTraversalOnArray(new Component[]{tfNombre, tfApellido1, tfApellido2, tfDNI, tfEmail, tfTelefono, btnSiguiente}));
		getContentPane().setFocusTraversalPolicy(new FocusTraversalOnArray(new Component[]{tfNombre, tfApellido1, tfApellido2, tfDNI, tfEmail, tfTelefono, btnSiguiente}));
		setFocusTraversalPolicy(new FocusTraversalOnArray(new Component[]{tfNombre, tfApellido1, tfApellido2, tfDNI, tfEmail, tfTelefono, btnSiguiente}));
	
	
	}

	protected void Comprobar() {
	
		if(tfNombre.getText().equals("")){
			JOptionPane.showMessageDialog(this, "El campo del nombre es obligatorio", "Campo obligatorio", JOptionPane.WARNING_MESSAGE);
			tfNombre.requestFocusInWindow();
		}
		else if(tfApellido1.getText().equals("")){
			JOptionPane.showMessageDialog(this, "El campo del primer apellido es obligatorio", "Campo obligatorio", JOptionPane.WARNING_MESSAGE);
			tfApellido1.requestFocusInWindow();
		}
		else if(tfApellido2.getText().equals("")){
			JOptionPane.showMessageDialog(this, "El campo del segundo apellido es obligatorio", "Campo obligatorio", JOptionPane.WARNING_MESSAGE);
			tfApellido2.requestFocusInWindow();
		}
		else if(tfDNI.getText().equals("")){
			JOptionPane.showMessageDialog(this, "El campo del dni es obligatorio", "Campo obligatorio", JOptionPane.WARNING_MESSAGE);
			tfDNI.requestFocusInWindow();
		}
		else if(tfEmail.getText().equals("")){
			JOptionPane.showMessageDialog(this, "El campo de email es obligatorio", "Campo obligatorio", JOptionPane.WARNING_MESSAGE);
			tfEmail.requestFocusInWindow();
		}
		else{
			Persona persona = new Persona(tfDNI.getText(), tfNombre.getText(), tfApellido1.getText(), tfApellido2.getText(),
					tfEmail.getText());
			if(!tfTelefono.getText().equals("")){
				persona.setTelefono(tfTelefono.getText());
			}
			else {
				persona.setTelefono("0");
			}
			
			//comprueba si existe en la base de datos
			if(!control.comprobar(persona)){ //si no existe ya, seguimos
				new HuellaPinFrame(persona).setVisible(true);
				this.dispose();
			}
			else {
				JOptionPane.showMessageDialog(this, "El usuario que intentas registrar ya tiene una cuenta.", "Error", JOptionPane.ERROR_MESSAGE);
			}
		}
	}

	protected void Limpiar() {
		tfNombre.setText("");
		tfApellido1.setText("");
		tfApellido2.setText("");
		tfDNI.setText("");
		tfEmail.setText("");
		tfTelefono.setText("");

		tfNombre.requestFocusInWindow();
	}
}
