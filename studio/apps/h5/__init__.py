from flask import Blueprint,render_template,request
import random
h5 = Blueprint("h5",__name__,template_folder="templates",static_folder="static")

@h5.route('/72years',methods=['GET','POST'])
def celeb_72_form():
    return render_template('dut72years_form.html')

@h5.route('/72years/card',methods=['GET','POST'])
def celeb_72_card():
    data = dict(request.values)
    back_images = ['orange.png']
    if data['wish'] =='others':
        data['wish'] = data['wish_other']
    image = random.sample(back_images,1)


    return render_template('dut72years_card.html',data=data,image=image)

