from memeer import app

if __name__ == '__main__':
    # import greplin.scales.flaskhandler as statserver
    # statserver.serveInBackground(8765, serverName='memeer-stats')

    app.debug = True
    app.run(host="127.0.0.1")
else:
    # gunicorn
    application = app
