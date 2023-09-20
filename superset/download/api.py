import logging
import datetime
import pathlib
import base64
from typing import Any, Dict
from flask import request, Response, jsonify, make_response
from flask_appbuilder import expose
from weasyprint import HTML, CSS
from superset.views.base_api import BaseSupersetApi, statsd_metrics

logger = logging.getLogger(__name__)

class DownloadRestApi(BaseSupersetApi):
    resource_name = "download"
    openapi_spec_tag = "Download"
    csrf_exempt = True

    @expose("/download/", methods=["POST", "GET"])
    def post(self) -> Response:
        """Response
        Returns the images supplied in a formatted PDF file
        ---
        post:
          description: >-
            Returns the dashboard's embedded configuration
          parameters:
          - in: body
            schema:
              type: string array
            name: image_urls
            description: The base64 data urls of the images to be converted
          - in: body
            schema:
              type: string
            name: report_name
            description: The name of the report
          - in: body
            schema:
              type: number
            name: width
            description: The width of the report
          - in: body
            schema:
              type: number
            name: height
            description: The height of the report, excluding the header and footer
          - in: body
            schema:
              type: string
            name: date
            description: The date string
          responses:
            200:
              description: The base data url string
              content:
                application/json:
                  schema:
                    type: string
        """

        image_urls = request.json.get('image_urls', [])
        report_name = request.json.get('report_name', '')
        width = request.json.get('width', 612)
        height = request.json.get('height', 590)
        date = request.json.get('date', datetime.date.today().strftime('%d.%m.%Y'))

        def get_file_data_url(filename):
          with open(f'{pathlib.Path(__file__).parent.absolute()}/{filename}', 'rb') as file:
            return base64.b64encode(file.read()).decode('UTF-8')

        zerofox_logo_text_url = get_file_data_url('zerofox-logo-white.png')
        foxy_url = get_file_data_url('foxy.png')

        def get_report_html():
          image_article_string = '\n'.join([f'''
            <article>
              <div class='header'>
                <img src="data:application/pdf;base64,{zerofox_logo_text_url}"></img>
                <hr />
                {report_name}
              </div>
              <div class='body'>
                <img src="data:application/pdf;base64,{x}"></img>
              </div>
              <div class='footer'>
                <img src="data:application/pdf;base64,{foxy_url}"></img>
                <br /><br />
                © ZeroFox 2023
              </div>
              <div class='page-count'>Page {i + 1}</div>
            </article>
          ''' for i, x in enumerate(image_urls)])
          return f'''
            <html>
              <article id="cover">
                <span>
                  <img src="data:application/pdf;base64,{zerofox_logo_text_url}"></img>
                  <hr />
                  {report_name}
                  <br />
                  {date}
                </span>
              </article>

              {image_article_string}
            </html>
          '''
        
        def get_report_css():
          return f'''
            body {{
              margin: 0;
              padding: 0;
              font-family: Open Sans;
              font-size: 14px;
              font-weight: 600;
              line-height: 19px;
              letter-spacing: 0em;
              text-align: left;
            }}

            @page {{
              margin: 0;
              padding: 0;
              width: {width}px;
              height: {height + 202}px;
            }}

            @page :first {{
              background-size: cover;
              background-image: linear-gradient(140deg, #253B4A, #367583);
            }}

            article {{
              display: block;
              page-break-after: always;
            }}

            #cover {{
              text-align: center;
              color: #FFFFFF;
            }}

            #cover span {{
              display: inline-block;
              vertical-align: middle;
              position: absolute;
              top: 50%;
              margin-top: -40px;
              width: 100%;
            }}

            #cover img {{
              width: 33%;
              object-fit: contain;
            }}

            #cover hr {{
              width: 33%;
            }}

            .header {{
              background-image: linear-gradient(140deg, #253B4A, #367583);
              text-align: center;
              color: #FFFFFF;
              height: 105px;
              font-family: Open Sans;
              font-size: 14px;
              font-weight: 600;
              line-height: 19px;
              letter-spacing: 0em;
            }}

            .header img {{
              padding-top: 17px;
              padding-bottom: 0px;
              width: 200px;
              object-fit: contain;
            }}

            .header hr {{
              width: 33%;
            }}

            .body {{
              height: {height}px;
              background: #FFFFFF;
            }}

            .body img {{
              width: {width}px;
              object-fit: contain;
            }}

            .footer {{
              background: #253B4A;
              text-align: center;
              color: #FFFFFF;
              height: 97px;
              position: absolute;
              bottom: 0;
              width: 100%;
              font-family: Open Sans;
              font-size: 12px;
              font-weight: 400;
              line-height: 16px;
              letter-spacing: 0em;         
            }}

            .footer img {{
              padding-top: 19px;
              padding-bottom: 0px;
              width: 36px;
              object-fit: contain;
            }}

            .page-count {{
              padding: 8px;
              border-radius: 8px;
              position: absolute;
              bottom: 24px;
              right: 24px;
              background: #4B626E;
              font-family: Open Sans;
              font-size: 14px;
              font-weight: 600;
              line-height: 19px;
              letter-spacing: 0em;
              text-align: left;
              color: #FFFFFF;
            }}
          '''

        HTML(string=get_report_html()).write_pdf('/tmp/temp.pdf', stylesheets=[CSS(string=get_report_css())])

        pdf_url = ''
        with open('/tmp/temp.pdf', 'rb') as pdf_file:
            pdf_url = f'''data:application/pdf;base64,{base64.b64encode(pdf_file.read()).decode('UTF-8')}'''
        return self.response(200, result=pdf_url)
