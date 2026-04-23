from flask_mail import Message
from app.mail import mail_service
from app.loggers import email_logger
from flask import current_app
import os

# Función para enviar correo a la empresa con los datos de la solicitud y archivos adjuntos
def send_email_company(datos, archivos):
    try :
        asunto = f"Solicitud de {datos['servicio']} - SadCont"

        hmtl_body = dessign_email_company(datos)

        msg = Message(
            subject=asunto,
            recipients=["pozodiaz@outlook.es"],  # correo empresa
            html=hmtl_body,
            sender=(current_app.config["COMPANY_NAME"], current_app.config["MAIL_DEFAULT_SENDER"])
        )
            
        # Adjuntar archivos
        for key, archivo in archivos.items():
            with open(archivo[0], "rb") as f:
                msg.attach(
                    filename=os.path.basename(archivo[0]),
                    content_type="application/octet-stream",
                    data=f.read()
                )

        mail_service.send(msg)
        
        email_logger.info({
            "event": "send_email",
            "recipient": "pozodiaz@outlook.es",
            "subject": f"Solicitud de {datos['servicio']} - SadCont",
            "status": "sent"
        })
    except Exception as e:
        email_logger.error(
            f"Error enviando correo a empresa: {str(e)}",
            exc_info=True
        )
        raise e
    


# Función para enviar correo al cliente con resumen de la solicitud
def send_email_client(subject, data, recipient):
    try:
        html_body = dessign_email_client(data)

        msg = Message(
            subject=subject,
            sender=(
                current_app.config["COMPANY_NAME"],
                current_app.config["MAIL_DEFAULT_SENDER"]
            ),
            recipients=[recipient],
            html=html_body
        )

        mail_service.send(msg)

        email_logger.info({
            "event": "send_email",
            "recipient": recipient,
            "subject": subject,
            "status": "sent"
        })

    except Exception as e:
        email_logger.error(
            f"Error enviando correo a {recipient}: {str(e)}",
            exc_info=True
        )
        raise e


def dessign_email_company(datos):
    body = f"""
    <!DOCTYPE html>
    <html lang="es">

    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Firma Electronica - SAD&CONT</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=Playfair+Display:wght@700&display=swap');

            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}


            body {{
                background-color: #eef2f6;
                font-family: 'DM Sans', 'Segoe UI', Tahoma, sans-serif;
                color: #2d3748;
                -webkit-font-smoothing: antialiased;
            }}

            .wrapper {{
            width: 100%;
            padding: 20px 5px;
            background-color: #f0f0f0;
        }}

        .container {{
            max-width: 580px;
            margin: 0 auto;
            background-color: #f2fff7;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 4px 24px rgba(29, 81, 114, 0.12);
        }}
        /* ── HEADER ── */
        .header {{
            background: linear-gradient(150deg, #1d5172 0%, #0f7b62 100%);
            padding: 30px 32px 28px;
            position: relative;
            overflow: hidden;
            color: #ecfffe;
        }}

        .header p {{
            font-family: 'Playfair Display', serif;
            font-size: 20px;
            font-weight: 700;
            margin-top: 8px;
        }}

        .header span {{
            font-size: 16px;
            color: #cbd5e0;
            margin-top: 4px;
            display: block;
        }}

        /* ── CONTENT ── */
        .content {{
            padding: 36px 32px 28px;
        }}

        h3 {{
            font-size: 20px;
            font-weight: 1000;
            margin-bottom: 16px;
            color: #1d6f72;
        }}

        .data {{
            margin: 10px 0px;
            padding: 16px;
            background-color: #d0d9e1;
            border-radius: 8px;
            font-size: 15px;
            border: 1px solid #7586a0;
        }}

        .parameter {{
            color: #000000d3;
        }}

        .dato {{
            font-weight: 800;
            color: #0b53c7;
        }}

        /* ── FOOTER ── */
        .footer {{
            background-color: #f7fafc;
            padding: 20px 32px;
            text-align: center;
            font-size: 14px;
            color: #a0aec0;
        }}

        /* ── MEDIA QUERIES ── */
        @media (max-width: 480px) {{

            .content,
            .header {{
                padding: 24px 15px;
            }}

            .footer {{
                padding: 16px 5px;
            }}
        }}
        </style>
    </head>

    <body>
        <div class="wrapper">
            <div class="container">
                <div class="header">
                    SAD&CONT
                    <p>Nueva Solicitud</p>
                    <span>{datos['servicio']}</span>
                </div>
                <div class="content">
                    <h3>Datos de la solicitud</h3>
                    <div class="data">
                        <p><span class="parameter">Servicio:</span> <span class="dato">{ datos['servicio'] }</span></p>
                        <p><span class="parameter">Tipo:</span> <span class="dato">{ datos['tipoPersona'] }</span></p>
                        <p><span class="parameter">Vigencia:</span> <span class="dato">{ datos['vigencia'] }</span></p>
                        <p><span class="parameter">Costo:</span> <span class="dato">{ datos['precio'] }</span></p>
                        <p><span class="parameter">Nombres:</span> <span class="dato">{ datos['nombres'] }</span></p>
                        <p><span class="parameter">Cedula:</span> <span class="dato">{ datos['identificacion'] }</span></p>
                        <p><span class="parameter">Celular:</span> <span class="dato">{ datos['celular'] }</span></p>
                        <p><span class="parameter">Correo:</span> <span class="dato">{ datos['correo'] }</span></p>
                    </div>
                    <br>
                    <h4>Verifique los archivos adjuntos</h4>
                </div>
                <div class="footer">
                    <p>© 2026 SAD&CONT. Todos los derechos reservados.</p>
                </div>
            </div>
        </div>
    </body>

    </html>
    """
    return body

def dessign_email_client(data):

    body = f"""
    <!DOCTYPE html>
    <html lang="es">

    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Confirmación de Adquisición – SADCONT</title>
        <!--[if mso]><noscript><xml><o:OfficeDocumentSettings><o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings></xml></noscript><![endif]-->
        <style>
            @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=Playfair+Display:wght@700&display=swap');

            * {{   
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                background-color: #eef2f6;
                font-family: 'DM Sans', 'Segoe UI', Tahoma, sans-serif;
                color: #2d3748;
                -webkit-font-smoothing: antialiased;
            }}

            .wrapper {{
                width: 100%;
                padding: 40px 5px;
                background-color: #eef2f6;
            }}

            .container {{
                max-width: 580px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 4px 24px rgba(29, 81, 114, 0.12);
            }}

            /* ── HEADER ── */
            .header {{
                background: linear-gradient(150deg, #1d5172 0%, #0f7b62 100%);
                padding: 36px 32px 28px;
                position: relative;
                overflow: hidden;
            }}

            .header::before {{
                content: '';
                position: absolute;
                top: -40px;
                right: -40px;
                width: 200px;
                height: 200px;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.06);
            }}

            .header::after {{
                content: '';
                position: absolute;
                bottom: -60px;
                left: -20px;
                width: 160px;
                height: 160px;
                border-radius: 50%;
                background: rgba(52, 199, 171, 0.15);
            }}

            .brand {{
                display: flex;
                align-items: center;
                gap: 12px;
                margin-bottom: 24px;
                position: relative;
                z-index: 1;
            }}

            .brand img {{
                width: 44px;
                height: 44px;
                border-radius: 10px;
                object-fit: cover;
                border: 2px solid rgba(255, 255, 255, 0.3);
            }}

            .brand-name {{
                font-family: 'Playfair Display', Georgia, serif;
                font-size: 26px;
                color: #ffffff;
                letter-spacing: -0.5px;
            }}

            .header-badge {{
                display: inline-flex;
                align-items: center;
                gap: 6px;
                background: rgba(52, 199, 171, 0.2);
                border: 1px solid rgba(52, 199, 171, 0.4);
                color: #7eecd8;
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 1.2px;
                text-transform: uppercase;
                padding: 5px 12px;
                border-radius: 20px;
                position: relative;
                z-index: 1;
            }}

            .header-badge::before {{
                content: '';
                width: 6px;
                height: 6px;
                border-radius: 50%;
                background: #34c7ab;
            }}

            .header-title {{
                font-family: 'Playfair Display', Georgia, serif;
                font-size: 30px;
                color: #ffffff;
                margin-top: 14px;
                line-height: 1.25;
                position: relative;
                z-index: 1;
            }}

            .header-subtitle {{
                color: rgba(255, 255, 255, 0.65);
                font-size: 14px;
                margin-top: 6px;
                position: relative;
                z-index: 1;
            }}

            /* ── CONTENT ── */
            .content {{
                padding: 36px 32px;
            }}

            .greeting {{
                font-size: 15px;
                color: #4a5568;
                margin-bottom: 20px;
            }}

            .greeting strong {{
                color: #1d5172;
                font-weight: 600;
            }}

            .intro-text {{
                font-size: 15px;
                color: #4a5568;
                line-height: 1.7;
                margin-bottom: 28px;
            }}

            /* ── SERVICE CARD ── */
            .service-card {{
                background: linear-gradient(135deg, #f0fdf9 0%, #e8f4fd 100%);
                border: 1px solid #b2e8dd;
                border-radius: 12px;
                padding: 24px;
                margin-bottom: 28px;
                position: relative;
                overflow: hidden;
            }}

            .service-card::after {{
                content: '✓';
                position: absolute;
                right: 20px;
                top: 50%;
                transform: translateY(-50%);
                font-size: 48px;
                color: rgba(20, 150, 122, 0.1);
                font-weight: 900;
                line-height: 1;
            }}

            .service-label {{
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 1px;
                text-transform: uppercase;
                color: #14967a;
                margin-bottom: 8px;
            }}

            .service-name {{
                font-family: 'Playfair Display', Georgia, serif;
                font-size: 22px;
                color: #1d5172;
                margin-bottom: 6px;
            }}

            .service-status {{
                display: inline-flex;
                align-items: center;
                gap: 5px;
                font-size: 12px;
                font-weight: 600;
                color: #0f7b62;
                background: #d1fae5;
                padding: 3px 10px;
                border-radius: 12px;
            }}

            /* ── STEPS ── */
            .steps-title {{
                font-size: 13px;
                font-weight: 600;
                letter-spacing: 0.8px;
                text-transform: uppercase;
                color: #718096;
                margin-bottom: 16px;
            }}

            .steps {{
                gap: 0;
                margin-bottom: 28px;
            }}

            .step {{
                display: flex;
                gap: 16px;
                align-items: flex-start;
                padding: 14px 0;
                border-bottom: 1px dashed #e2e8f0;
            }}

            .step:last-child {{
                border-bottom: none;
            }}

            .step-num {{
                margin-top: 2px;
                margin-right: 8px;
                color: #14967a;
                font-weight: 700;
                font-size: 16px;
            }}

            .step-text {{
                padding-top: 6px;
            }}

            .step-text strong {{
                display: block;
                font-size: 14px;
                color: #2d3748;
                margin-bottom: 2px;
            }}

            .step-text span {{
                font-size: 13px;
                color: #718096;
            }}

            /* ── CTA ── */
            .cta-wrap {{
                text-align: center;
                margin-bottom: 28px;
            }}

            .cta-button {{
                display: inline-block;
                background: linear-gradient(135deg, #1d5172 0%, #14967a 100%);
                color: #ffffff !important;
                padding: 14px 36px;
                text-decoration: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 600;
                letter-spacing: 0.3px;
                box-shadow: 0 4px 16px rgba(29, 81, 114, 0.3);
            }}

            .support-note {{
                background: #f7fafc;
                border-radius: 10px;
                padding: 18px 20px;
                text-align: center;
                font-size: 13px;
                color: #718096;
                line-height: 1.6;
            }}

            .support-note a {{
                color: #1d5172;
                font-weight: 600;
                text-decoration: none;
            }}

            /* ── DIVIDER ── */
            .divider {{
                height: 1px;
                background: linear-gradient(to right, transparent, #e2e8f0, transparent);
                margin: 0 32px 0;
            }}

            /* ── FOOTER ── */
            .footer {{
                padding: 24px 32px;
                text-align: center;
            }}

            .footer-brand {{
                font-family: 'Playfair Display', Georgia, serif;
                font-size: 16px;
                color: #1d5172;
                margin-bottom: 8px;
            }}

            .footer p {{
                font-size: 12px;
                color: #a0aec0;
                line-height: 1.6;
            }}

            .footer a {{
                color: #14967a;
                text-decoration: none;
            }}

            .footer-copy {{
                margin-top: 16px;
                padding-top: 16px;
                border-top: 1px solid #edf2f7;
                font-size: 11px;
                color: #cbd5e0;
            }}

            /* ── RESPONSIVE ── */
            @media (max-width: 480px) {{
                .content,
                .header {{
                    padding: 24px 5px;
                }}

                .footer {{
                    padding: 20px;
                }}

                .header-title {{
                    font-size: 24px;
                }}
            }}
        </style>
    </head>

    <body>
        <div class="wrapper">
            <div class="container">

                <!-- HEADER -->
                <div class="header">
                    <div class="brand">
                        <span class="brand-name">SADCONT</span>
                    </div>
                    <div class="header-badge">Solicitud recibida</div>
                    <h1 class="header-title">¡Tu solicitud ha sido<br>registrada con éxito!</h1>
                    <p class="header-subtitle">Confirmación automática · SADCONT</p>
                </div>

                <!-- CONTENT -->
                <div class="content">
                    <p class="greeting">Hola, <strong>{data['nombres']}</strong> 👋</p>
                    <p class="intro-text">
                        Hemos recibido correctamente tu solicitud de adquisición de servicio. A continuación encontrarás el
                        resumen y los próximos pasos que seguirá nuestro equipo.
                    </p>

                    <!-- Service Card -->
                    <div class="service-card">
                        <div class="service-label">Servicio solicitado</div>
                        <div class="service-name">{data['servicio']}</div>
                        <div class="service-status">● En proceso</div>
                    </div>

                    <!-- Next Steps -->
                    <div class="steps-title">¿Qué sigue ahora?</div>
                    <div class="steps">
                        <div class="step">
                            <div class="step-num">1</div>
                            <div class="step-text">
                                <strong>Revisión de solicitud</strong>
                                <span>Nuestro equipo revisará los datos ingresados en tu solicitud.</span>
                            </div>
                        </div><br>
                        <div class="step">
                            <div class="step-num">2</div>
                            <div class="step-text">
                                <strong>Contacto personalizado</strong>
                                <span>Si tu solicitud es aprobada, nuestro equipo se pondrá en contacto contigo por correo para la activación del servicio.</span>
                            </div>
                        </div><br>
                        <div class="step">
                            <div class="step-num"><div>3</div></div>
                            <div class="step-text">
                                <strong>Activación del servicio</strong>
                                <span>Una vez verificados los datos, activaremos tu servicio de Firma Digital.</span>
                            </div>
                        </div>
                    </div>

                    <!-- CTA -->
                    <div class="cta-wrap">
                        <a href="https://sadcont.com" class="cta-button">Ver Mas Servicios</a>
                    </div>

                    <!-- Support Note -->
                    <div class="support-note">
                        ¿Tienes alguna duda? Escríbenos a
                        <br><a href="mailto:soporte@sadcont.com">sadcont@outlook.com</a>
                        <br><a href="https://api.whatsapp.com/send?phone=593963488065" target="_blank">0963474086</a>.
                    </div>

                </div><!-- /content -->

                <div class="divider"></div>

                <!-- FOOTER -->
                <div class="footer">
                    <div class="footer-brand">SADCONT</div>
                    <p>
                        Gracias por confiar en nuestros servicios.<br>
                        Este correo fue generado automáticamente, por favor <strong>no respondas</strong> a este mensaje.
                    </p>
                    <div class="footer-copy">
                        © 2026 SADCONT. Todos los derechos reservados.<br>
                    </div>
                </div>

            </div><!-- /container -->
        </div><!-- /wrapper -->
    </body>

    </html>
    """
    return body