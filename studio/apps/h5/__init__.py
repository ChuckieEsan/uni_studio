from flask import Blueprint,render_template
h5 = Blueprint("h5",__name__,template_folder="templates",static_folder="static")

@h5.route('/72years',methods=['GET','POST'])
def celeb_72_form():
    return render_template('dut72years_form.html')

@h5.route('/72years/card',methods=['GET','POST'])
def celeb_72_card():
    return render_template('dut72years_card.html')