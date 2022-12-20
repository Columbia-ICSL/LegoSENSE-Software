import os
import stat
import time
import glob
import zipfile
import datetime
import humanize
from flask import render_template, make_response, send_file, redirect
from flask.views import MethodView

LOG_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'log')


def install(server):
    def get_type(mode):
        if stat.S_ISDIR(mode) or stat.S_ISLNK(mode):
            type = 'dir'
        else:
            type = 'file'
        return type

    @server.template_filter('size_fmt')
    def size_fmt(size):
        return humanize.naturalsize(size)

    @server.template_filter('time_fmt')
    def time_desc(timestamp):
        mdate = datetime.datetime.fromtimestamp(timestamp)
        str = mdate.strftime('%Y-%m-%d %H:%M:%S')
        return str

    @server.template_filter('time_humanize')
    def time_humanize(timestamp):
        mdate = datetime.datetime.utcfromtimestamp(timestamp)
        return humanize.naturaldelta(datetime.datetime.utcfromtimestamp(time.time()) - mdate, months=True,
                                     minimum_unit='seconds') + ' ago'

    class PathView(MethodView):
        def get(self, p=''):
            path = os.path.join(LOG_FOLDER, p)
            if os.path.isdir(path):
                contents = []
                total = {'size': 0, 'dir': 0, 'file': 0}
                for filename in os.listdir(path):
                    if not filename.endswith('.csv'):
                        continue
                    # if filename in ignored:
                    #     continue
                    filepath = os.path.join(path, filename)
                    stat_res = os.stat(filepath)
                    info = {}
                    info['name'] = filename
                    info['mtime'] = stat_res.st_mtime
                    ft = get_type(stat_res.st_mode)
                    info['type'] = ft
                    total[ft] += 1
                    sz = stat_res.st_size
                    info['size'] = sz
                    total['size'] += sz
                    contents.append(info)

                # Sort by mtime
                contents_sorted = sorted(contents, key=lambda item: item['mtime'], reverse=True)

                page = render_template('data/main.html', segment='data', path=p, contents=contents_sorted, total=total)
                res = make_response(page, 200)
            elif os.path.isfile(path):
                if not path.endswith('.csv'):
                    return make_response('You can only access csv files.', 400)
                # TODO: Restrict file extension to .csv and .log?
                print(f"Sending file {path}")
                res = send_file(path, as_attachment=True)
            elif p == "zip_data":
                current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                zip_file_name = f'data_{current_time}.zip'
                zip_file_path = os.path.join('/tmp/', zip_file_name)

                # Zip all the .csv files in the /data folder
                with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
                    for file in glob.glob(os.path.join(LOG_FOLDER, '*.csv')):
                        zip_file.write(file, os.path.basename(file))
                res = send_file(zip_file_path, as_attachment=True)
            else:
                res = make_response('Not found', 404)
            return res

    class DeleteDataView(MethodView):
        def get(self, p=''):
            path = os.path.join(LOG_FOLDER, p)
            if os.path.isfile(path):
                if not path.endswith('.csv'):
                    return make_response('You can only delete csv files.', 400)
                else:
                    print(f'Deleting {path}')
                    os.rename(path, path+'.trash')
                res = redirect('/data', code=302)
            else:
                res = make_response('Not found', 404)
            return res

    path_view = PathView.as_view('path_view')
    delete_data_view = DeleteDataView.as_view('delete_data_view')
    server.add_url_rule('/data', view_func=path_view)
    server.add_url_rule('/data/<path:p>', view_func=path_view)
    server.add_url_rule('/delete_data/<path:p>', view_func=delete_data_view)