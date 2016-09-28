package view;

import java.awt.Color;
import java.awt.Font;
import java.awt.Image;
import java.awt.Insets;
import java.awt.Rectangle;
import java.awt.Toolkit;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.Icon;
import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JPasswordField;
import javax.swing.SwingConstants;
import javax.swing.SwingUtilities;
import javax.swing.border.LineBorder;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.digitalpersona.onetouch.DPFPGlobal;
import com.digitalpersona.onetouch.capture.DPFPCapture;
import com.digitalpersona.onetouch.capture.event.DPFPDataAdapter;
import com.digitalpersona.onetouch.capture.event.DPFPDataEvent;
import com.digitalpersona.onetouch.capture.event.DPFPErrorAdapter;
import com.digitalpersona.onetouch.capture.event.DPFPErrorEvent;
import com.digitalpersona.onetouch.capture.event.DPFPReaderStatusAdapter;
import com.digitalpersona.onetouch.capture.event.DPFPReaderStatusEvent;

import controller.Controller;
import entity.Persona;

public class HuellaPinFrame extends JFrame {
	private final String ID_TERMINAL = "AB001";
	private JPanel panelTextoHuella, panelHuella, panelTextoPin, panelPin;
	private JLabel lblHuella, lblTextoHuella, lblIntroduceTuPin;	
	private JButton btnRepetir, btnBorrar, btnAtras, btnLimpiar, btnSiguiente;
	private JPasswordField pfPin;
	
	//Nos sirve para identificar al dispositivo
	private DPFPCapture Lector = DPFPGlobal.getCaptureFactory().createCapture();
	
	//Logger
	private Logger logger = LoggerFactory.getLogger(HuellaPinFrame.class); 
	
	private Controller control = new Controller();
	
	private Persona persona;

	public HuellaPinFrame(Persona p) {
		persona = p;
		
		setIconImage(Toolkit.getDefaultToolkit().createImage(this.getClass().getClassLoader().getResource("images/fingerPay.png")));
		setResizable(false);
		setTitle("Registro huella y pin | FingerPay");
		
		setBounds(new Rectangle(300, 200, 750, 400));
		getContentPane().setLayout(null);
		
		panelTextoHuella = new JPanel();
		panelTextoHuella.setBorder(new LineBorder(new Color(0, 0, 0), 1, true));
		panelTextoHuella.setBounds(10, 11, 413, 51);
		getContentPane().add(panelTextoHuella);
		panelTextoHuella.setLayout(null);
		
		lblTextoHuella = new JLabel("Pon tu dedo sobre el lector de huellas");
		lblTextoHuella.setHorizontalAlignment(SwingConstants.CENTER);
		lblTextoHuella.setFont(new Font("Tahoma", Font.PLAIN, 18));
		lblTextoHuella.setBounds(10, 11, 393, 29);
		panelTextoHuella.add(lblTextoHuella);
		
		panelHuella = new JPanel();
		panelHuella.setBorder(new LineBorder(new Color(0, 0, 0), 1, true));
		panelHuella.setBounds(10, 73, 413, 279);
		getContentPane().add(panelHuella);
		panelHuella.setLayout(null);
		
		lblHuella = new JLabel();
		lblHuella.setBorder(new LineBorder(new Color(0, 0, 0)));
		lblHuella.setBounds(10, 11, 263, 257);
		panelHuella.add(lblHuella);
		
		Icon iconRep = new ImageIcon(getClass().getResource("/images/repetir.png"));
		btnRepetir = new JButton("Repetir huella", iconRep);
		btnRepetir.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				borrarHuella();
			}
		});
		btnRepetir.setBounds(283, 72, 120, 125);
		btnRepetir.setVerticalTextPosition(SwingConstants.BOTTOM);
		btnRepetir.setToolTipText("Repetir la captura de huella");
		btnRepetir.setMargin(new Insets(0, 0, 0, 0));
		btnRepetir.setHorizontalTextPosition(SwingConstants.CENTER);
		btnRepetir.setFont(new Font("Tahoma", Font.BOLD, 15));
		panelHuella.add(btnRepetir);

		panelTextoPin = new JPanel();
		panelTextoPin.setBorder(new LineBorder(new Color(0, 0, 0), 1, true));
		panelTextoPin.setBounds(433, 11, 291, 51);
		getContentPane().add(panelTextoPin);
		panelTextoPin.setLayout(null);
		
		lblIntroduceTuPin = new JLabel("Introduce tu pin");
		lblIntroduceTuPin.setHorizontalAlignment(SwingConstants.CENTER);
		lblIntroduceTuPin.setFont(new Font("Tahoma", Font.PLAIN, 18));
		lblIntroduceTuPin.setBounds(10, 11, 271, 29);
		panelTextoPin.add(lblIntroduceTuPin);

		panelPin = new JPanel();
		panelPin.setBorder(new LineBorder(new Color(0, 0, 0), 1, true));
		panelPin.setBounds(433, 73, 291, 120);
		getContentPane().add(panelPin);
		panelPin.setLayout(null);
		
		pfPin = new JPasswordField();
		pfPin.setFont(new Font("Tahoma", Font.PLAIN, 40));
		pfPin.setBounds(10, 40, 140, 40);
		panelPin.add(pfPin);

		btnBorrar = new JButton("Borrar");
		btnBorrar.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				borrarPin();
			}
		});
		btnBorrar.setToolTipText("Borra el pin");
		btnBorrar.setFont(new Font("Tahoma", Font.BOLD, 15));
		btnBorrar.setBounds(154, 40, 127, 40);
		panelPin.add(btnBorrar);
		
		
		Icon iconAtras= new ImageIcon(getClass().getResource("/images/back.png"));
		btnAtras = new JButton(iconAtras);
		btnAtras.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				atras();
			}
		});
		btnAtras.setBounds(433, 230, 90, 90);
		getContentPane().add(btnAtras);
		btnAtras.setVerticalTextPosition(SwingConstants.BOTTOM);
		btnAtras.setToolTipText("Paso anterior");
		btnAtras.setMargin(new Insets(0, 0, 0, 0));
		btnAtras.setHorizontalTextPosition(SwingConstants.CENTER);
		
		Icon iconLim = new ImageIcon(getClass().getResource("/images/clear.png"));
		btnLimpiar = new JButton(iconLim);
		btnLimpiar.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				limpiarTodo();
			}
		});
		btnLimpiar.setVerticalTextPosition(SwingConstants.BOTTOM);
		btnLimpiar.setToolTipText("Limpia huella y pin");
		btnLimpiar.setMargin(new Insets(0, 0, 0, 0));
		btnLimpiar.setHorizontalTextPosition(SwingConstants.CENTER);
		btnLimpiar.setBounds(534, 231, 90, 90);
		getContentPane().add(btnLimpiar);
		
		Icon iconSig = new ImageIcon(getClass().getResource("/images/next.png"));
		btnSiguiente = new JButton(iconSig);
		btnSiguiente.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				siguiente();
			}
		});
		btnSiguiente.setVerticalTextPosition(SwingConstants.BOTTOM);
		btnSiguiente.setToolTipText("Siguiente paso");
		btnSiguiente.setMargin(new Insets(0, 0, 0, 0));
		btnSiguiente.setHorizontalTextPosition(SwingConstants.CENTER);
		btnSiguiente.setBounds(634, 229, 90, 90);
		getContentPane().add(btnSiguiente);
		
		
		
		
		
		Iniciar();
		start();
	}

	protected void Iniciar(){
		Lector.addDataListener(new DPFPDataAdapter(){
			@Override
			public void dataAcquired(final DPFPDataEvent e){
				SwingUtilities.invokeLater(new Runnable() {
			        @Override
			        public void run() {
			    		logger.info("La huella ha sido capturada");
			    		Image imghuella = control.ProcesarCaptura(e.getSample(), ID_TERMINAL);
						if(imghuella != null){
							stop();
							mostrarImagen(imghuella);
						}
	        		}
				});
			}
		});
		
	  Lector.addReaderStatusListener(new DPFPReaderStatusAdapter(){
	    @Override public void readerConnected(final DPFPReaderStatusEvent e){
	      SwingUtilities.invokeLater(new Runnable() {
	        @Override
	        public void run() {
	        	logger.info("El sensor de huella dactilar se encuentra Activado");
	        }
	      });
	    }
	    @Override public void readerDisconnected(final DPFPReaderStatusEvent e){
	      SwingUtilities.invokeLater(new Runnable() {
	        @Override
	        public void run() {
	        	logger.error("El sensor de huella dactilar se encuentra Desactivado");
	        }
	      });
	    }
	  });
	  Lector.addErrorListener(new DPFPErrorAdapter(){
	    @SuppressWarnings("unused")
		public void errorReader(final DPFPErrorEvent e){
	      SwingUtilities.invokeLater(new Runnable() {
	        @Override
	        public void run() {
	        	logger.error("Error: " + e.getError());
	        }
	      });
	    }
	  });
	}
	
	public void start(){
		Lector.startCapture();
		logger.info("Utilizando lector de huella dactilar");
	}
		
	public void stop(){
		Lector.stopCapture();
		logger.info("Lector detenido");
	}
	
	private void siguiente() {
		if(lblHuella.getIcon() == null){
			JOptionPane.showMessageDialog(this, "Tienes que registrar una huella", "Error", JOptionPane.WARNING_MESSAGE);
		}
		else if(new String(pfPin.getPassword()).equals("")){
			JOptionPane.showMessageDialog(this, "Tienes que escribir un pin", "Error", JOptionPane.WARNING_MESSAGE);
		}
		else{	
			persona.setPin(new String(pfPin.getPassword()));
			control.generaTxt(persona, ID_TERMINAL);
		}
	}

	private void limpiarTodo() {
		borrarHuella();
		borrarPin();
	}

	private void borrarPin() {
		pfPin.setText("");		
	}

	private void borrarHuella() {
		lblHuella.setIcon(null);
		start();
	}

	private void atras() {
		stop();
		new Principal(persona).setVisible(true);
		this.dispose();
	}
	
	private void mostrarImagen(Image image){
		 this.lblHuella.setIcon(
    		new ImageIcon(
    			image.getScaledInstance(this.lblHuella.getHeight(), this.lblHuella.getHeight(), Image.SCALE_SMOOTH)
			)
    	);
	}
}
