from flask import render_template
from . import app
import werkzeug

############################################################
# ERROR ROUTE :: BAD REQUEST :: 400
# STATUS :: TODO
############################################################
@app.errorhandler(400)
def error_400(error):
    return render_template('errors/400.html'), 400

############################################################
# ERROR ROUTE :: FORBIDDEN :: 403
# STATUS :: TODO
############################################################
@app.errorhandler(403)
def error_403(error):
    return render_template('errors/403.html'), 403

############################################################
# ERROR ROUTE :: NOT FOUND :: 404
# STATUS :: IMPLEMENTED ... somewhat
############################################################
@app.errorhandler(404)
@app.errorhandler(werkzeug.exceptions.BadRequest)
def error_404(error):
    return render_template('errors/404.html'), 404


############################################################
# ERROR ROUTE :: GENERAL SERVER ERROR :: 500
# STATUS :: TODO
############################################################
@app.errorhandler(500)
def error_500(error):
    return render_template('errors/500.html'), 500