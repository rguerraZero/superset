import logging
import datetime
import pathlib
import base64
from flask import current_app, request, Response
from flask_appbuilder import expose
from weasyprint import HTML, CSS
from superset.views.base_api import BaseSupersetApi
from superset.zf_integration.prometheus import PDF_SUCCESS_COUNTER, PDF_FAILURE_COUNTER

import boto3
import uuid
import os

logger = logging.getLogger(__name__)

env = os.environ.get('ENV')
app = os.environ.get('SUPERSET_ACCESS_METHOD')


class DownloadRestApi(BaseSupersetApi):
    resource_name = 'download'
    openapi_spec_tag = 'Download'
    csrf_exempt = True

    @expose('/download/', methods=['POST', 'GET'])
    def post(self) -> Response:
        '''Response
        Returns the images supplied in a formatted PDF file
        ---
        post:
          description: >-
            Returns the images supplied in a formatted PDF file
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
            500:
              $ref: '#/components/responses/500'
        '''
        try:
            image_urls = request.json.get('image_urls', [])
            report_name = request.json.get('report_name', '')
            date = request.json.get(
                'date', datetime.date.today().strftime('%d.%m.%Y'))

            def get_file_data_url(filename):
                with open(f'{pathlib.Path(__file__).parent.absolute()}/{filename}', 'rb') as file:
                    return f'''data:application/pdf;base64,{base64.b64encode(file.read()).decode('UTF-8')}'''

            self.zerofox_logo_text_url = get_file_data_url(
                'zerofox-logo-white.png')
            self.foxy_url = get_file_data_url('foxy.png')
            pdf_pages = self.get_pdf_pages(report_name, date, image_urls)
            pdf_id = str(uuid.uuid4())
            file_name = f'{pdf_id}.pdf'
            self.write_pdf(pdf_pages, file_name)
            pdf_url = ""
            for attempt in range(current_app.config["UPLOAD_PDF_TO_S3_TRIES"]):
                try:
                    pdf_url = self.upload_to_s3(file_name)
                except:
                    logger.error(
                        "Error at trying to upload report file to S3.")
                    continue
                break
            else:
                raise Exception("Error at upload the pdf file to S3.")
            PDF_SUCCESS_COUNTER.inc()
            return self.response(200, result=pdf_url)
        except Exception as e:
            PDF_FAILURE_COUNTER.inc()
            return self.response(500, message=f'Error generating report: {e}')

    def get_pdf_pages(self, report_name, date, image_urls):
        pdf_pages = []
        pdf_pages.append(HTML(string=self.get_report_page(report_name, date)).render(
            stylesheets=[CSS(string=self.get_report_css(995, 1728, 'linear-gradient(140deg, #253B4A, #367583)'))]))
        for i, x in enumerate(image_urls):
            width, height = self.get_page_dimension(image_urls[x])
            pdf_pages.append(HTML(string=self.get_tab_html(report_name, image_urls[x], page=i)).render(
                stylesheets=[CSS(string=self.get_report_css(width, height, '#f7f7f7'))]))
        return pdf_pages

    def get_report_page(self, report_name, date):
        return f'''
        <html>
          <article id='cover'>
            <span>
              <img src='{self.zerofox_logo_text_url}'></img>
              <hr />
              {report_name}
              <br />
              {date}
            </span>
          </article>
        </html>
      '''

    def get_tab_html(self, report_name, image, page):
        return f'''
        <html>
          <article >
            <div class='header'>
              <img src='{self.zerofox_logo_text_url}'></img>
              <hr />
              {report_name}
            </div>
            <div>
              <img src='{image['dataUrl']}'></img>
            </div>
            <div class='footer'>
              <img src='{self.foxy_url}'></img>
              <br /><br />
              © ZeroFox 2023
            </div>
            <div class='page-count'>Page {page + 1}</div>
          </article>
        </html
        '''

    def write_pdf(self, pdf_pages, file_name):
        document = pdf_pages[0]
        pages = []
        for doc in pdf_pages:
            for page in doc.pages:
                pages.append(page)
        document.copy(pages).write_pdf(f'/tmp/{file_name}')

    def upload_to_s3(self, file_name):
        bucket_name = f'superset-{app}-pdfs-{env}'
        s3 = boto3.client('s3')
        with open(f'/tmp/{file_name}', 'rb') as f:
            s3.upload_fileobj(f, bucket_name, file_name)
        bucket_location = s3.get_bucket_location(Bucket=bucket_name)
        pdf_url = "https://s3-{0}.amazonaws.com/{1}/{2}".format(
            bucket_location['LocationConstraint'],
            bucket_name,
            file_name)
        return pdf_url

    def get_page_dimension(self, page_configuration):
        width = max([995, page_configuration['width']])
        height = max([1728, page_configuration['height']])
        return width, height

    def get_report_css(self, width, height, background):
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
          background-image: {background};
          background-color: #f7f7f7;
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
          background: #f7f7f7;
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
