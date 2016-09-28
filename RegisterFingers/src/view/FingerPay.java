package view;

import java.awt.Color;
import java.awt.Component;
import java.awt.Font;
import java.awt.HeadlessException;
import java.awt.Image;
import java.awt.Insets;
import java.awt.Toolkit;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.image.RenderedImage;
import java.io.File;
import java.io.IOException;

import javax.imageio.ImageIO;
import javax.swing.Icon;
import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.SwingConstants;
import javax.swing.SwingUtilities;
import javax.swing.border.EmptyBorder;
import javax.swing.border.LineBorder;

import com.digitalpersona.onetouch.DPFPDataPurpose;
import com.digitalpersona.onetouch.DPFPFeatureSet;
import com.digitalpersona.onetouch.DPFPGlobal;
import com.digitalpersona.onetouch.DPFPSample;
import com.digitalpersona.onetouch.DPFPTemplate;
import com.digitalpersona.onetouch.capture.DPFPCapture;
import com.digitalpersona.onetouch.capture.event.DPFPDataAdapter;
import com.digitalpersona.onetouch.capture.event.DPFPDataEvent;
import com.digitalpersona.onetouch.capture.event.DPFPErrorAdapter;
import com.digitalpersona.onetouch.capture.event.DPFPErrorEvent;
import com.digitalpersona.onetouch.capture.event.DPFPReaderStatusAdapter;
import com.digitalpersona.onetouch.capture.event.DPFPReaderStatusEvent;
import com.digitalpersona.onetouch.processing.DPFPFeatureExtraction;
import com.digitalpersona.onetouch.processing.DPFPImageQualityException;


public class FingerPay extends JFrame{
	private int indiceDedo;
	private String nombre, intento;
	private JPanel contentPane, panelHuellas, panelAcciones;
	private JLabel lblHuella, lblMI, lblAI, lblCI, lblII, lblPI, lblMD, lblAD, lblCD, lblID, lblPD, lblRojo, lblNaranja, lblVerde;
	private Image img;
	private JButton btnRepetirActual;
	
	//Nos sirve para identificar al dispositivo
	private DPFPCapture Lector = DPFPGlobal.getCaptureFactory().createCapture();
	//La plantilla, nueva o rescatada
	private DPFPTemplate template;
	//A modo de CONSTANTE para crear plantillas
	public String TEMPLATE_PROPERTY = "template";
	//Para leer la huella, y definirla como una verificación
	public DPFPFeatureSet featureSetVerificacion;
	
	public FingerPay(String nombre, String intento) throws HeadlessException {
		setIconImage(Toolkit.getDefaultToolkit().createImage(this.getClass().getClassLoader().getResource("icono/huellas1.png")));
		setResizable(false);
		setTitle("Pago dactilar | FingerPay");
		
		this.nombre = nombre;
		this.intento = intento;

		setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
		setBounds(100, 100, 439, 505);
		
		this.indiceDedo = 0;
		
		this.contentPane = new JPanel();
		this.contentPane.setBorder(new EmptyBorder(5, 5, 5, 5));
		this.contentPane.setLayout(null);
		setContentPane(this.contentPane);
		
		this.panelHuellas = new JPanel();
		this.panelHuellas.setBorder(new LineBorder(new Color(0, 0, 0), 2, true));
		this.panelHuellas.setAlignmentX(Component.RIGHT_ALIGNMENT);
		this.panelHuellas.setBounds(75, 10, 283, 279);
		this.panelHuellas.setLayout(null);
		this.contentPane.add(this.panelHuellas);
		
		this.lblHuella = new JLabel();
		this.lblHuella.setBounds(10, 11, 261, 257);
		this.panelHuellas.add(this.lblHuella);
		
		this.panelAcciones = new JPanel();
		this.panelAcciones.setBounds(10, 289, 412, 167);
		this.contentPane.add(this.panelAcciones);
		this.panelAcciones.setLayout(null);
		
		this.lblMI = new JLabel("dedo meñique izquierdo");
		this.lblMI.setBounds(153, 0, 135, 16);
		this.lblMI.setForeground(Color.RED);
		this.panelAcciones.add(this.lblMI);

		this.lblAI = new JLabel("dedo anular izquierdo");
		this.lblAI.setBounds(153, 16, 135, 16);
		this.lblAI.setForeground(Color.RED);
		this.panelAcciones.add(this.lblAI);

		this.lblCI = new JLabel("dedo corazon izquierdo");
		this.lblCI.setAlignmentY(Component.TOP_ALIGNMENT);
		this.lblCI.setBounds(153, 32, 135, 16);
		this.lblCI.setForeground(Color.RED);
		this.panelAcciones.add(this.lblCI);

		this.lblII = new JLabel("dedo indice izquierdo");
		this.lblII.setBounds(153, 48, 135, 16);
		this.lblII.setForeground(Color.RED);
		this.panelAcciones.add(this.lblII);

		this.lblPI = new JLabel("dedo pulgar izquierdo");
		this.lblPI.setBounds(153, 64, 135, 16);
		this.lblPI.setForeground(Color.RED);
		this.panelAcciones.add(this.lblPI);
		
		this.lblPD = new JLabel("dedo pulgar derecho");
		this.lblPD.setBounds(153, 80, 135, 16);
		this.lblPD.setForeground(Color.RED);
		this.panelAcciones.add(this.lblPD);

		this.lblID = new JLabel("dedo indice derecho");
		this.lblID.setBounds(153, 96, 135, 16);
		this.lblID.setForeground(Color.RED);
		this.panelAcciones.add(this.lblID);

		this.lblCD = new JLabel("dedo corazon derecho");
		this.lblCD.setBounds(153, 112, 135, 16);
		this.lblCD.setForeground(Color.RED);
		this.panelAcciones.add(this.lblCD);

		this.lblAD = new JLabel("dedo anular derecho");
		this.lblAD.setBounds(153, 130, 135, 16);
		this.lblAD.setForeground(Color.RED);
		this.panelAcciones.add(this.lblAD);

		this.lblMD = new JLabel("dedo meñique derecho");
		this.lblMD.setBounds(153, 146, 135, 16);
		this.lblMD.setForeground(Color.RED);
		this.panelAcciones.add(this.lblMD);
		
		this.lblRojo = new JLabel("SIN REGISTRAR");
		this.lblRojo.setFont(new Font("Tahoma", Font.BOLD, 11));
		this.lblRojo.setForeground(Color.RED);
		this.lblRojo.setBounds(300, 30, 100, 14);
		this.panelAcciones.add(this.lblRojo);
		
		this.lblNaranja = new JLabel("EN PROGRESO");
		this.lblNaranja.setFont(new Font("Tahoma", Font.BOLD, 11));
		this.lblNaranja.setForeground(Color.ORANGE);
		this.lblNaranja.setBounds(300, 80, 100, 14);
		this.panelAcciones.add(this.lblNaranja);
		
		this.lblVerde = new JLabel("REGISTRADO");
		this.lblVerde.setFont(new Font("Tahoma", Font.BOLD, 11));
		this.lblVerde.setForeground(Color.GREEN);
		this.lblVerde.setBounds(300, 130, 100, 14);
		panelAcciones.add(this.lblVerde);
		
		Icon icon = new ImageIcon(new ImageIcon(FingerPay.class.getResource("/icono/repetir.png")).getImage().getScaledInstance(100, 100, Image.SCALE_DEFAULT));
		this.btnRepetirActual = new JButton("Repetir Actual", icon);
		btnRepetirActual.setFont(new Font("Tahoma", Font.BOLD, 15));
		this.btnRepetirActual.setVerticalTextPosition(SwingConstants.BOTTOM);
		this.btnRepetirActual.setHorizontalTextPosition(SwingConstants.CENTER);
		this.btnRepetirActual.setMargin(new Insets(0, 0, 0, 0));
		this.btnRepetirActual.setBounds(10, 13, 120, 143);
		panelAcciones.add(this.btnRepetirActual);
		this.btnRepetirActual.addActionListener(new ActionListener() {
			
			@Override
			public void actionPerformed(ActionEvent e) {
				repetir();
			}
		});
		
		
		Iniciar();
		start();
		actualizaLblDedo(Color.ORANGE);
	}
	
	protected void Iniciar(){
	  Lector.addDataListener(new DPFPDataAdapter(){
	    @Override public void dataAcquired(final DPFPDataEvent e){
	      SwingUtilities.invokeLater(new Runnable() {
	        @Override
	        public void run() {
	          EnviarTexto("La huella ha sido capturada");
	          ProcesarCaptura(e.getSample());}
	        });
	      }
	    });
	  Lector.addReaderStatusListener(new DPFPReaderStatusAdapter(){
	    @Override public void readerConnected(final DPFPReaderStatusEvent e){
	      SwingUtilities.invokeLater(new Runnable() {
	        @Override
	        public void run() {
	          EnviarTexto("El sensor de huella dactilar se encuentra Activado");
	        }
	      });
	    }
	    @Override public void readerDisconnected(final DPFPReaderStatusEvent e){
	      SwingUtilities.invokeLater(new Runnable() {
	        @Override
	        public void run() {
	          EnviarTexto("El sensor de huella dactilar se encuentra Desactivado");
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
	          EnviarTexto("Error: " + e.getError());
	        }
	      });
	    }
	  });
	}
	
	public void ProcesarCaptura(DPFPSample muestra){
		
		this.featureSetVerificacion = extraerCaracteristicas(muestra, DPFPDataPurpose.DATA_PURPOSE_VERIFICATION);
		if(this.featureSetVerificacion != null){
  	    	DibujarHuella(CrearImagenHuella(muestra));
			stop();
	        EnviarTexto("La plantilla de huella ha sido creada. Puede Verificar o Identificarla");
	        guardar();
	        actualizaLblDedo(Color.GREEN);
	        indiceDedo++;
	        actualizaLblDedo(Color.ORANGE);
	        if(indiceDedo < 10)
	        	start();
	        else if(JOptionPane.showConfirmDialog(this, "Desdeas REPETIR el meñique derecho", "Repetir?", JOptionPane.YES_NO_OPTION) == JOptionPane.YES_OPTION)
	        	repetir();
	        else dispose();
		}
	}
	
	public DPFPFeatureSet extraerCaracteristicas(DPFPSample muestra, DPFPDataPurpose motivo){
		DPFPFeatureExtraction extractor = DPFPGlobal.getFeatureExtractionFactory().createFeatureExtraction();
		try{
		  return extractor.createFeatureSet(muestra, motivo);
		} catch (DPFPImageQualityException e) {
		  System.out.println(e.getMessage());
		  return null;
		}
	}
	
	public Image CrearImagenHuella(DPFPSample muestra){
		this.img = DPFPGlobal.getSampleConversionFactory().createImage(muestra);
		
		return img;
	}
	
	private void actualizaLblDedo(Color color) {
		switch (this.indiceDedo) {
			case 0: lblMI.setForeground(color); break;
			case 1: lblAI.setForeground(color); break;
			case 2: lblCI.setForeground(color); break;
			case 3: lblII.setForeground(color); break;
			case 4: lblPI.setForeground(color); break;
			case 5: lblPD.setForeground(color); break;
			case 6: lblID.setForeground(color); break;
			case 7: lblCD.setForeground(color); break;
			case 8: lblAD.setForeground(color); break;
			case 9: lblMD.setForeground(color); break;
		}
	}

	public void EnviarTexto(String mensaje){
	}
	
	public void start(){
	  Lector.startCapture();
	  EnviarTexto("Utilizando lector de huella dactilar");
	}
	
	public void stop(){
	  Lector.stopCapture();
	  EnviarTexto("Lector detenido");
	}
	
	public void DibujarHuella(Image image){	    
	    this.lblHuella.setIcon(
    		new ImageIcon(
				//image.getScaledInstance(this.lblHuella.getHeight(), this.lblHuella.getHeight(), Image.SCALE_DEFAULT)
    			image.getScaledInstance(this.lblHuella.getHeight(), this.lblHuella.getHeight(), Image.SCALE_SMOOTH)
			)
    	);
	}
	
	public void setTemplate(DPFPTemplate template) {
	  DPFPTemplate antigua = this.template;
	  this.template = template;
	  firePropertyChange(TEMPLATE_PROPERTY, antigua, template);
	}
	
	public DPFPTemplate getTemplate(){
		return template;
	}
	
	private void guardar() {
		try {
			ImageIO.write((RenderedImage) this.img, "jpg", new File("dedos/"+ intento + nombre + "_" + Integer.toString(this.indiceDedo) + ".jpg"));
		} catch (IOException e) {
			e.printStackTrace();
		}
		
	}
	
	private void repetir() {
		if(indiceDedo > 0){
			stop();
	        actualizaLblDedo(Color.RED);
	        indiceDedo--;
	        actualizaLblDedo(Color.ORANGE);
	        start();
		}
	}
}


