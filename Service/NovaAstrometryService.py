#Basic stuff
import json
import logging
from pathlib import Path
import time

#webservice stuff
import urllib

# Forging request
import base64
from io import StringIO
from email.generator import Generator
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.application  import MIMEApplication
from email.encoders import encode_noop

class NovaAstrometryService(object):
  """ Nova Astrometry Service """
  # API request engine
  defaultAPIURL = 'http://nova.astrometry.net/api/'

  def __init__(self, configFileName=None, logger=None, apiURL=defaultAPIURL):
    self.logger = logger or logging.getLogger(__name__)

    if configFileName is None:
      # Default file is ~/.nova.json
      home = Path.home()
      config = home / '.nova.json'
      self.configFileName = str(config)
    else:
      self.configFileName = configFileName

    # Now configuring
    self.logger.debug('Configuring Nova Astrometry Service with file %s',\
      self.configFileName)

    # Get key from json
    with open(self.configFileName) as jsonFile:  
      data = json.load(jsonFile)
      self.key = data['key']

    # Api URL
    self.apiURL=apiURL
    # Manage persistent session/submissions/jobs with cookie like ID
    self.session = None
    self.submissionId = None
    self.jobId = None
    self.solvedId = None

    # Finished configuring
    self.logger.debug('Configured Nova Astrometry service successfully')

  def getAPIUrl(self, service):
    return self.apiURL + service


  def login(self):
    args = { 'apikey' : self.key }
    result = self.sendRequest('login', args)
    session = result['session']
    self.logger.debug('Nova Astrometry Service: Got session '+str(session))
    if not session:
      self.logger.error('Nova Astrometry Service: No session in result')
    self.session = session

  def getSubmissionStatus(self, subId, justdict=False):
    result = self.sendRequest('submissions/%s' % subId)
    if justdict:
      return result
    return result['status']

  def getJobStatus(self, job_id, justdict=False):
    result = self.sendRequest('jobs/%s' % job_id)
    if justdict:
      return result
    stat = result.get('status')
    if stat == 'success':
      result = self.sendRequest('jobs/%s/calibration' % job_id)
      self.logger.debug('Nova Astrometry Service, Calibration result:',
        result)
      result = self.sendRequest('jobs/%s/info' % job_id)
      self.logger.debug('Nova Astrometry Service, Calibration:', result)
    return stat

  def solveImage(self, fitsFile, coordSky=None, confidence=None):
    '''Center (RA, Dec):  (179.769, 45.100)
    Center (RA, hms): 11h 59m 04.623s
    Center (Dec, dms):  +45° 06' 01.339"
    Size: 25.4 x 20.3 arcmin
    Radius: 0.271 deg
    Pixel scale:  1.19 arcsec/pixel
    Orientation:  Up is 90 degrees E of N
    '''
    args = dict(
      allow_commercial_use='d', # license stuff
      allow_modifications='d', # license stuff
      publicly_visible='y')#, # other can see request and data
      #scale_units='arcsecperpix', # unit for field size estimation
      #scale_type='ev', # from target value+error instead of bounds
      #scale_est=1.19, # estimated field scale in deg TODO Get from camera+scope
      #scale_err=2, #[0, 100] percentage of error on field
      #center_ra=180,#coordSky['ra']#float [0, 360] coordinate of image center TODO
      #center_dec=45,#coordSky['dec']#float [-90, 90] coordinate of image center on
                                  #right ascencion TODO
      #radius=1.0, # float in degrees around center_[ra,dec] TODO confidence
      #downsample_factor=4, # Ease star detection on images
      #tweak_order=2, # use order-2 polynomial for distortion correction
      #use_sextractor=False, # Alternative star extractor method
      #crpix_center=True, #Set the WCS  referenceto be the center pixel in image
      #parity=2) #geometric indication that can make detection faster (unused)
 
    # Now upload image
    upres = self.sendRequest('upload', args, fitsFile)
    stat = upres['status']
    if stat != 'success':
      self.logger.error('Nova Astrometry Service, upload failed: status '+\
        str(stat)+' and server response: '+str(upres))

    self.submissionId = upres['subid']
    self.logger.debug('Nova Astrometry Service, uploaded file successfully '+\
      ', got status '+str(stat)+' submission ID: '+str(self.submissionId))
    if self.solvedId is None:
      if self.submissionId is None:
        self.logger.error('Nova Astrometry Service : Can\'t --wait without '+\
          'a submission id or job id!')
      while True:
        stat = self.getSubmissionStatus(self.submissionId, justdict=True)
        self.logger.debug('Nova Astrometry service, status update for '+\
          ' submission ID '+str(self.submissionId)+' : '+str(stat))
        jobs = stat.get('jobs', [])
        if len(jobs):
          for j in jobs:
            if j is not None:
              break
          if j is not None:
            self.logger.debug('Nova Astrometry Service: got a solved job id '+\
              str(j))
            self.solvedId = j
            break
        time.sleep(1)

    while True:
      stat = self.getJobStatus(self.solvedId, justdict=True)
      self.logger.debug('Nova Astrometry Service, status update for job ID '+\
        str(self.solvedId)+' : '+str(stat))
      if stat['status'] in ['success']:
        success = True
        self.logger.debug('Nova Astrometry Service: server successfully '+\
          'solved job ID '+str(self.solvedId))
        break
      elif stat['status'] in ['failure']:
        success = False
        self.logger.debug('Nova Astrometry Service: server failed to solve '+\
          'job ID '+str(self.solvedId))
        break
      time.sleep(5)

    if self.solvedId:
      print('Yep, everything should be alright now')
      # we have a jobId for retrieving results

  def sendRequest(self, service, args={}, fileArgs=None):
    '''
      service: string
      args: dict
      fileArgs: tuple with filename, data
    '''
    if self.session is not None:
      args['session']=self.session
    argJson = json.dumps(args)
    url = self.getAPIUrl(service)
    self.logger.debug('Nova Astrometry Service, sending json: '+str(argJson))

    # If we're sending a file, format a multipart/form-data
    if fileArgs is not None:
      m1 = MIMEBase('text', 'plain')
      m1.add_header('Content-disposition', 'form-data; name="request-json"')
      m1.set_payload(argJson)

      #m2 = MIMEApplication(fileArgs,'octet-stream',encode_noop)
      m2 = MIMEApplication(open('frame0.fits','rb').read(),'octet-stream',encode_noop)
      m2.add_header('Content-disposition',
                    'form-data; name="file"; filename="frame0.fits"')
      mp = MIMEMultipart('form-data', None, [m1, m2])

      # Make a custom generator to format it the way we need.
      class MyGenerator(Generator):
        def __init__(self, fp, root=True):
          Generator.__init__(self, fp, mangle_from_=False, maxheaderlen=0)
          self.root = root
        def _write_headers(self, msg):
          # We don't want to write the top-level headers;
          # they go into Request(headers) instead.
          if self.root:
            return
          # We need to use \r\n line-terminator, but Generator
          # doesn't provide the flexibility to override, so we
          # have to copy-n-paste-n-modify.
          for h, v in msg.items():
            print(('%s: %s\r\n' % (h,v)), end='', file=self._fp)
          # A blank line always separates headers from body
          print('\r\n', end='', file=self._fp)

        # The _write_multipart method calls "clone" for the
        # subparts.  We hijack that, setting root=False
        def clone(self, fp):
          return MyGenerator(fp, root=False)

      fp = StringIO()
      g = MyGenerator(fp)
      g.flatten(mp)
      data = fp.getvalue().encode()
      headers = {'Content-type': mp['Content-type']}
      self.logger.debug('Nova Astrometry Service, sending binary file data'+\
        ' with headers: '+str(headers))
    else:
      # Else send x-www-form-encoded
      data = {'request-json': argJson}
      self.logger.debug('Nova Astrometry Service, sending text only data:'+\
        ' ,json version : '+str(argJson))
      data = urllib.parse.urlencode(data).encode("utf-8")
      self.logger.debug('Nova Astrometry Service, sending text only data:'+\
        ' ,encoded version : '+str(data))
      headers = {}

    req = urllib.request.Request(url=url, headers=headers, data=data)

    try:
      with urllib.request.urlopen(req) as response:
        txt = response.read()
        self.logger.debug('Nova Astrometry Service, Got json:'+
          str(txt))
        result = json.loads(txt)
        #self.logger.debug('Nova Astrometry Service, Got result:'+str(result))
        stat = result.get('status')
        #self.logger.debug('Nova Astrometry Service, Got status:'+str(stat))
        if stat == 'error':
          errstr = result.get('errormessage', '(none)')
          self.logger.error('Nova Astrometry Service error message: ' + errstr)
        return result
    except urllib.error.HTTPError as e:
      self.logger.error('Nova Astrometry Service, HTTPError', e)
      txt = e.read()
      open('err.html', 'wb').write(txt)
      self.logger.error('Nova Astrometry Service, Wrote error text to err.html')


    def submission_images(self, subid):
      result = self.sendRequest('submission_images', {'subid':subid})
      return result.get('image_ids')

    def myjobs(self):
      result = self.sendRequest('myjobs/')
      return result['jobs']


    def annotateData(self,job_id):
      """
        :param job_id: id of job
        :return: return data for annotations
       """
      result = self.sendRequest('jobs/%s/annotations' % job_id)
      return result


