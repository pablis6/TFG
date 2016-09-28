package view;

import javax.swing.JFrame;
import javax.swing.JTextField;
import javax.swing.JOptionPane;
import javax.swing.JRadioButton;
import javax.swing.SwingConstants;
import javax.swing.ButtonGroup;
import javax.swing.JTextArea;

import java.awt.Color;
import java.awt.Font;
import java.awt.Toolkit;

import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.border.LineBorder;
import javax.swing.JButton;

import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.awt.Component;

@SuppressWarnings("serial")
public class MainWindow extends JFrame{
	private JTextField tfNombre;
	private JRadioButton rdbtnPrimerRegistro, rdbtnSegundoRegistro;
	private final ButtonGroup buttonGroup = new ButtonGroup();
	private JTextArea txtrFingerpay;
	private JLabel lblNombre;
	private JLabel lblNumeroDeRegistro;
	private JPanel pNombre, pRegistro;
	private JButton btnEntrar;
	
	
	public MainWindow() {
		setIconImage(Toolkit.getDefaultToolkit().createImage(this.getClass().getClassLoader().getResource("icono/huellas1.png")));
		setResizable(false);
		setTitle("FingerPay");
		
		MainWindow me = this;
		getContentPane().setLayout(null);
		this.setBounds(450, 200, 500, 300);
		
		pNombre = new JPanel();
		pNombre.setBorder(new LineBorder(new Color(0, 0, 0), 1, true));
		pNombre.setBounds(43, 82, 181, 137);
		getContentPane().add(pNombre);
		pNombre.setLayout(null);
		
		tfNombre = new JTextField();
		tfNombre.setBounds(50, 83, 86, 20);
		tfNombre.setColumns(10);
		tfNombre.requestFocusInWindow();
		pNombre.add(tfNombre);
		
		lblNombre = new JLabel("Nombre:");
		lblNombre.setAlignmentX(Component.RIGHT_ALIGNMENT);
		lblNombre.setBounds(50, 28, 86, 14);
		pNombre.add(lblNombre);
		
		pRegistro = new JPanel();
		pRegistro.setBorder(new LineBorder(new Color(0, 0, 0), 1, true));
		pRegistro.setBounds(241, 82, 200, 137);
		getContentPane().add(pRegistro);
		pRegistro.setLayout(null);
		
		rdbtnPrimerRegistro = new JRadioButton("Primer registro");
		rdbtnPrimerRegistro.setAlignmentX(Component.CENTER_ALIGNMENT);
		rdbtnPrimerRegistro.setBounds(39, 57, 142, 23);
		pRegistro.add(rdbtnPrimerRegistro);
		buttonGroup.add(rdbtnPrimerRegistro);
		
		rdbtnSegundoRegistro = new JRadioButton("Segundo registro");
		rdbtnSegundoRegistro.setAlignmentX(Component.CENTER_ALIGNMENT);
		rdbtnSegundoRegistro.setBounds(39, 89, 142, 23);
		pRegistro.add(rdbtnSegundoRegistro);
		buttonGroup.add(rdbtnSegundoRegistro);
		rdbtnSegundoRegistro.setHorizontalAlignment(SwingConstants.LEFT);
		
		rdbtnPrimerRegistro.setSelected(true);
		
		lblNumeroDeRegistro = new JLabel("Numero de registro");
		lblNumeroDeRegistro.setAlignmentX(Component.CENTER_ALIGNMENT);
		lblNumeroDeRegistro.setBounds(39, 24, 142, 14);
		pRegistro.add(lblNumeroDeRegistro);
		
		txtrFingerpay = new JTextArea();
		txtrFingerpay.setText("FingerPay \r\npara guardar una huella escribe un nombre\r\ny selecciona un intento");
		txtrFingerpay.setToolTipText("");
		txtrFingerpay.setBorder(new LineBorder(new Color(0, 0, 0), 1, true));
		txtrFingerpay.setEditable(false);
		txtrFingerpay.setFont(new Font("Monospaced", Font.BOLD, 15));
		txtrFingerpay.setBackground(Color.WHITE);
		txtrFingerpay.setBounds(43, 7, 398, 66);
		getContentPane().add(txtrFingerpay);
		
		this.addWindowListener(new WindowAdapter() {
			public void windowOpened(WindowEvent e ){
				tfNombre.requestFocus();
			}
			public void windowGainedFocus(WindowEvent e) {
				btnEntrar.requestFocus();
			}
		});
		
		
		btnEntrar = new JButton("Entrar");
		btnEntrar.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				if(tfNombre.getText().isEmpty())
					JOptionPane.showMessageDialog(me, "Introduce un nombre correcto", "Error", JOptionPane.ERROR_MESSAGE);
				else{
					String intento = "";
					if(rdbtnPrimerRegistro.isSelected()){
						intento = "F";
						btnEntrar.requestFocus();
					}
					if(rdbtnSegundoRegistro.isSelected()){
						intento = "S";			
					}
					new FingerPay(tfNombre.getText(), intento).setVisible(true);
					
				}
			}
		});
		btnEntrar.setBounds(352, 228, 89, 23);
		getContentPane().add(btnEntrar);
	}
}
