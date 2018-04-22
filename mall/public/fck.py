from flask import request,url_for,current_app,send_from_directory,redirect
from werkzeug.utils import secure_filename
from flask_login import current_user
from mall.extensions import ckeditor,csrf_protect

import datetime,os


from .import blueprint



@blueprint.route('/ckeditorfiles/<path:filename>')
@csrf_protect.exempt
def ckeditorfiles(filename):
    path = os.getcwd()+'/'+current_app.config['CKEDITOR_FILE_UPLOAD_URL']
    return send_from_directory(path, filename)


@blueprint.route('/upload', methods=['GET','POST'])
@csrf_protect.exempt
@ckeditor.uploader
def upload():
    f = request.files.get('upload')
    filename = secure_filename(f.filename)

    dataetime = datetime.datetime.today().strftime('%Y%m%d')
    file_dir = '%s/%s/'%(current_user.id,dataetime)
    
    if not os.path.isdir(current_app.config['CKEDITOR_FILE_UPLOAD_URL']+file_dir):
        os.makedirs(current_app.config['CKEDITOR_FILE_UPLOAD_URL']+file_dir)
    
    f.save(current_app.config['CKEDITOR_FILE_UPLOAD_URL'] +file_dir+filename)
    filename = file_dir+filename

    url = url_for('.ckeditorfiles', filename=filename)
    return url



