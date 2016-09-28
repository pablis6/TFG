package view;

import java.awt.Color;
import java.awt.Font;
import java.awt.Image;
import java.awt.Insets;
import java.awt.Rectangle;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.Icon;
import javax.swing.ImageIcon;
import javax.swing.JFormattedTextField;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JPasswordField;
import javax.swing.JSeparator;
import javax.swing.JTextArea;
import javax.swing.SwingConstants;
import javax.swing.SwingUtilities;
import javax.swing.UIManager;

import org.apache.commons.lang3.StringUtils;
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

public class WindowTerminal extends JFrame {
	private final String ID_TERMINAL = "AA001";
	private JPasswordField pfPIN;
	private JPanel panelPay, panelCharging, panelResolution;
	private JLabel lblTextPrice, lblFingerPrint, lblPIN, lblLoading, lblTextLoading,lblSolution;
	private JSeparator separator1, separator2;
	private JTextArea taTextSolution;
	private Thread hebra;
	
	//Nos sirve para identificar al dispositivo
	private DPFPCapture Lector = DPFPGlobal.getCaptureFactory().createCapture();
	
	//Logger
	private Logger logger = LoggerFactory.getLogger(WindowTerminal.class); 
	
	private Controller control;
	private JFormattedTextField tfPrice;
	
	public WindowTerminal() {
		
		control = new Controller();
		
		setBounds(new Rectangle(0, 0, 230, 300));
		setResizable(false);
		setUndecorated(true);
		//Window components
		
		getContentPane().setLayout(null);
		
		panelPay = new JPanel();
		panelPay.setBounds(0, 0, 229, 300);
		getContentPane().add(panelPay);
		panelPay.setLayout(null);
		
		lblTextPrice = new JLabel("Precio total a pagar:");
		lblTextPrice.setBounds(10, 11, 208, 31);
		panelPay.add(lblTextPrice);
		lblTextPrice.setHorizontalAlignment(SwingConstants.CENTER);
		lblTextPrice.setFont(new Font("Tahoma", Font.PLAIN, 20));
		
		tfPrice = new JFormattedTextField();
		tfPrice.setCaretColor(UIManager.getColor("Panel.background"));
		tfPrice.setFont(new Font("Tahoma", Font.PLAIN, 40));
		tfPrice.setHorizontalAlignment(SwingConstants.CENTER);
		tfPrice.setBackground(UIManager.getColor("Panel.background"));
		tfPrice.setBorder(null);
		tfPrice.setBounds(10, 42, 208, 62);
		panelPay.add(tfPrice);
		tfPrice.setColumns(10);
		
		separator1 = new JSeparator();
		separator1.setBounds(10, 104, 208, 2);
		panelPay.add(separator1);
		
		lblFingerPrint = new JLabel("");
		lblFingerPrint.setBounds(83, 115, 72, 90);
		panelPay.add(lblFingerPrint);
		lblFingerPrint.setHorizontalAlignment(SwingConstants.CENTER);
		lblFingerPrint.setEnabled(false);
		
		separator2 = new JSeparator();
		separator2.setBounds(10, 215, 208, 2);
		panelPay.add(separator2);
		
		lblPIN = new JLabel("PIN");
		lblPIN.setBounds(10, 216, 208, 31);
		panelPay.add(lblPIN);
		lblPIN.setHorizontalAlignment(SwingConstants.CENTER);
		lblPIN.setFont(new Font("Tahoma", Font.PLAIN, 20));
		
		pfPIN = new JPasswordField();
		pfPIN.setCaretColor(UIManager.getColor("PasswordField.background"));
		pfPIN.setMargin(new Insets(0, 0, 0, 0));
		pfPIN.setHorizontalAlignment(SwingConstants.CENTER);
		pfPIN.setFont(new Font("Tahoma", Font.PLAIN, 40));
		pfPIN.setBounds(10, 248, 208, 42);
		panelPay.add(pfPIN);
		pfPIN.setToolTipText("");
		pfPIN.setEditable(false);

		panelCharging = new JPanel();
		panelCharging.setBackground(Color.WHITE);
		panelCharging.setBounds(0, 0, 229, 300);
		getContentPane().add(panelCharging);
		panelCharging.setLayout(null);
		panelCharging.setVisible(false);
		
		
		Icon load = new ImageIcon(getClass().getResource("/images/fingerprintmini.gif"));
		lblLoading = new JLabel(load);
		lblLoading.setBounds(27, 60, 175, 175);
		panelCharging.add(lblLoading);
		
		lblTextLoading = new JLabel("Conectando con el servidor...");
		lblTextLoading.setHorizontalAlignment(SwingConstants.CENTER);
		lblTextLoading.setBounds(27, 235, 175, 20);
		panelCharging.add(lblTextLoading);
		
		panelResolution = new JPanel();
		panelResolution.setBounds(0, 0, 229, 300);
		getContentPane().add(panelResolution);
		panelResolution.setLayout(null);
		panelResolution.setVisible(false);
		
		lblSolution = new JLabel("");
		lblSolution.setHorizontalAlignment(SwingConstants.CENTER);
		lblSolution.setBounds(27, 60, 175, 175);
		panelResolution.add(lblSolution);
		
		taTextSolution = new JTextArea();
		taTextSolution.setFont(new Font("Arial", Font.PLAIN, 13));
		taTextSolution.setWrapStyleWord(true);
		taTextSolution.setLineWrap(true);
		taTextSolution.setBorder(null);
		taTextSolution.setEditable(false);
		taTextSolution.setBackground(UIManager.getColor("Panel.background"));
		taTextSolution.setBounds(10, 235, 209, 40);
		panelResolution.add(taTextSolution);
		//End window coponents
		
		//main program
		
		//write price
		logger.info("Comienza la introducción de precio");
		tfPrice.requestFocusInWindow();
		estadoHuella(Color.ORANGE);			
		
		tfPrice.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {			
				//read fingerprint
				logger.info("Comienza la lectura de huella");
				lblFingerPrint.setEnabled(true);
				lblFingerPrint.requestFocusInWindow();
				Iniciar();
				start();
			}
		});		
		
		//write pin
		pfPIN.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				
				panelPay.setVisible(false);
				panelCharging.setVisible(true);
				
				hebra = new Thread(new HiloMonitoriza());
				hebra.start();
				
			}
		});
	}
	
	protected void Iniciar(){
		Lector.addDataListener(new DPFPDataAdapter(){
			@Override
			public void dataAcquired(final DPFPDataEvent e){
				SwingUtilities.invokeLater(new Runnable() {
			        @Override
			        public void run() {
			    		logger.info("La huella ha sido capturada");
						if(control.ProcesarCaptura(e.getSample(), ID_TERMINAL)){
							  stop();
							  estadoHuella(Color.GREEN);

							  pfPIN.setEditable(true);

							  pfPIN.requestFocusInWindow();
							  
						}
						else {
							estadoHuella(Color.RED);
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
	
	private void estadoHuella(Color color) {
		Image image = null;
		if(color == Color.GREEN){
			image = new ImageIcon(getClass().getResource("/images/FingerprintVerde.png")).getImage();
		}
		else if(color == Color.RED){
			image = new ImageIcon(getClass().getResource("/images/FingerprintRojo.png")).getImage();
			
		}
		else if(color == Color.ORANGE){
			image = new ImageIcon(getClass().getResource("/images/Fingerprintnaranja.png")).getImage();
			
		}
		
		lblFingerPrint.setIcon(
				new ImageIcon(
						image.getScaledInstance(this.lblFingerPrint.getWidth(), this.lblFingerPrint.getHeight(), Image.SCALE_SMOOTH)
				)
		);
		
	}
	
	private class HiloMonitoriza implements Runnable{

		public HiloMonitoriza(){}
		
		@Override
		public void run() {
			//generar txt
			control.generaTxt(ID_TERMINAL, new String(pfPIN.getPassword()), tfPrice.getText());
	           
			//enviar cosas
			
			//esperar hasta tener respuestas
			String valoracion = control.monitorizar();
			try {
				mostrarValoracion(valoracion);
			} catch (InterruptedException e) {
				logger.error(e.getMessage());
			}
			
		}		
	}

	public void mostrarValoracion(String valoracion) throws InterruptedException {
		hebra.interrupt();
		panelCharging.setVisible(false);
		panelResolution.setVisible(true);
		
		String[] val = StringUtils.split(valoracion, "|");
		
		Image image = new ImageIcon(getClass().getResource("/images/"+ val[0] +".png")).getImage();
		lblSolution.setIcon(
			new ImageIcon(
					image.getScaledInstance(this.lblSolution.getWidth(), this.lblSolution.getHeight(), Image.SCALE_SMOOTH)
			)
		);
		
		taTextSolution.setText(val[1]);
		Thread.sleep(5000);
		
		panelResolution.setVisible(false);
		panelPay.setVisible(true);
		
		tfPrice.setText("");
		
		lblFingerPrint.setEnabled(false);
		estadoHuella(Color.ORANGE);
		
		pfPIN.setText("");
		
		logger.info("Comienza la introducción de precio");
		tfPrice.requestFocusInWindow();
	}
}
