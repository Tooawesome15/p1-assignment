from main import app

if __name__ == '__main__':
    app.run(debug = True)
    # app.run(host='172.18.186.183', debug=True, ssl_context=('cert.pem', 'key.pem'))