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
bucket_app_name = {
    'external': 'zf-dash',
    'internal': 'bi'
}
A4_PAGE_WIDTH = 793
A4_PAGE_HEIGHT = 1122
FOOTER_SIZE = 202


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
            self.zerofox_logo_text_url = get_file_data_url('ZFlogo.png')
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
            stylesheets=[CSS(string=self.get_report_css(A4_PAGE_WIDTH, A4_PAGE_HEIGHT, 'linear-gradient(300deg, #18325A 14.27%, #091F40 58.84%)'))]))
        for i, x in enumerate(image_urls):
            width, height = self.get_page_dimension(image_urls[x])
            pdf_pages.append(
                HTML(
                    string=self.get_tab_html(
                        report_name, image_urls[x], page=i, year=datetime.date.today().year)
                ).render(
                    stylesheets=[CSS(string=self.get_report_css(width, height, '#f7f7f7'))]))
        return pdf_pages

    def get_report_page(self, report_name, date):
        return f'''
        <html>
          <article id='cover'>
            <div style="padding-bottom: 8px;">
              <span class='cover-report-icon'>></span>
              <span class='cover-report-text'> REPORT</span>
            </div>
            <div class='cover-report-box'>
              <div class='cover-report-title'>{report_name}</div>
            </div>
            <div class='cover-report-date'>{date}</div>
            <img src='{self.zerofox_logo_text_url}'></img>
          </article>
        </html>
      '''

    def get_tab_html(self, report_name, image, page, year):
        return f'''
        <html>
          <article >
            <div class='header'>
              {report_name}
            </div>
            <div>
              <img src='{image['dataUrl']}'></img>
            </div>
            <div class='footer'>
              <div class='footer-date'>
                © ZeroFox {year}
              </div>
              <img class='footer-img' src='{self.foxy_url}'></img>
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
        bucket_name = self.get_bucket_name()
        s3 = boto3.client('s3')
        with open(f'/tmp/{file_name}', 'rb') as f:
            s3.upload_fileobj(f, bucket_name, file_name)
        bucket_location = s3.get_bucket_location(Bucket=bucket_name)
        pdf_url = "https://s3-{0}.amazonaws.com/{1}/{2}".format(
            bucket_location['LocationConstraint'],
            bucket_name,
            file_name)
        return pdf_url

    def get_bucket_name(self):
        return f'superset-{bucket_app_name[app]}-pdfs-{env}'

    def get_page_dimension(self, page_configuration):
        width = max([A4_PAGE_WIDTH, page_configuration['width']+FOOTER_SIZE])
        height = max(
            [A4_PAGE_HEIGHT, page_configuration['height']+FOOTER_SIZE])
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

        .cover-report-icon{{
          color: #89FCFE;
          font-size: 16px;
          font-family: Poppins;
          font-weight: 600;
        }}

        .cover-report-text {{
          color: white;
          font-size: 16px;
          font-family: Poppins;
          font-weight: 600;
        }}

        .cover-report-box {{
          padding: 8px;
          background: white;
          gap: 8px;
          display: inline-flex;
          max-width: 33%;
        }}

        .cover-report-title {{
          color: #D63C37;
          font-size: 16px;
          font-family: Poppins;
          font-weight: 600;
          word-wrap: break-word;
          max-width: 33%;
        }}

        .cover-report-date {{
          padding-top: 8px;
          color: white;
          font-size: 14px;
          font-family: Poppins;
          font-weight: 400;
        }}

        @page {{
          margin: 0;
          padding: 0;
          width: {width}px;
          height: {height}px;
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
          color: #FFFFFF;
          padding-top:204px;
          padding-left: 95px;
        }}

        #cover img {{
          width: 200px;
          height: 35px;
          flex-shrink: 0;
          position: absolute;
          right: 24px;
          bottom: 43px;
        }}

        .header {{
          background: linear-gradient(300deg, #18325A 14.27%, #091F40 58.84%);
          display: flex;
          width: 100%;
          height: 64px;
          padding: 21px 0px 22px 0px;
          justify-content: center;
          align-items: center;
          flex-shrink: 0;
          color: #FFF;
          font-family: Poppins;
          font-size: 14px;
          font-style: normal;
          font-weight: 600;
          line-height: normal;
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
          background: linear-gradient(300deg, #18325A 14.27%, #091F40 58.84%);
          flex-shrink: 0;
          color: #FFFFFF;
          height: 64px;
          position: absolute;
          bottom: 0;
          width: 100%;
          letter-spacing: 0em;
          color: #FFF;
          font-family: Poppins;
          font-size: 12px;
          font-style: normal;
          font-weight: 400;
          line-height: normal;
          text-align: center;
        }}

        .footer-date {{
          left: 32px;
          top: 23px;
          bottom: 23px;
          letter-spacing: 0em;
          color: #FFF;
          font-family: Poppins;
          font-size: 12px;
          font-style: normal;
          font-weight: 400;
          line-height: normal;
          position: absolute;
        }}

        .footer img {{
          padding-top: 15px;
          padding-bottom: 0px;
          width: 36px;
          object-fit: contain;
        }}

        .page-count {{
          padding: 8px;
          border-radius: 8px;
          position: absolute;
          bottom: 15px;
          right: 33px;
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
