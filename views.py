from django.shortcuts import render
from django.shortcuts import render, HttpResponse, redirect
from django.db import connection
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from . import views





def login(request):
    if request.method == "POST":
        userid = request.POST['userid']
        password = request.POST['password']
        cursor = connection.cursor()
        cursor.execute("select * from login where admin_id= '" + userid + "' AND password = '" + password + "'")
        admin = cursor.fetchone()
        if admin == None:
            cursor.execute("select * from volunteer where idvolunteer = '" + userid + "' AND password = '" + password + "' ")
            vol = cursor.fetchone()
            if vol == None:
                cursor.execute("select * from user_register where user_id = '" + userid + "' AND password = '" + password + "' ")
                user = cursor.fetchone()
                if user == None:
                        return HttpResponse("<script>alert('Invalid Userid or Password ');window.location='../login';</script>")
                else:
                    request.session['userid'] = userid
                    return redirect('user_home')
            else:
                cursor.execute("select * from volunteer where idvolunteer = '" + userid + "' AND password = '" + password + "' and status ='approved' ")
                vol1 = cursor.fetchone()
                if vol1 == None:
                    return HttpResponse("<script>alert('SORRY YOU ARE NOT APPROVED YET ');window.location='../login';</script>")
                else:
                    request.session['volid'] = userid
                    return redirect('vol_home')

        else:
            request.session['adminid'] = userid
            return redirect('admin_home')
    return render(request, "login.html")



def signup(request):
    if request.method == "POST":
        id = request.POST['name']
        name = request.POST['name']
        address = request.POST['address']
        phone = request.POST['phone']
        email = request.POST['email']
        password = request.POST['password']
        cursor = connection.cursor()
        cursor.execute("insert into user_register values ('"+str(id)+"','"+str(name)+"','" + str(address) + "','" + str(phone) + "', '" + str(email) + "', '" + str(password) + "') ")
        return HttpResponse("<script>alert('registered successfully');window.location='../login';</script>")

def signupvol(request):
    if request.method == "POST":
        name = request.POST['name']
        charity = request.POST['cname']
        address = request.POST['address']
        phone = request.POST['phone']
        email = request.POST['email']
        password = request.POST['psw']
        cursor = connection.cursor()
        cursor.execute("insert into volunteer values (null,'"+str(name)+"','" + str(address) + "','" + str(phone) + "', '" + str(email) + "', '" + str(password) + "','pending','"+str(charity)+"') ")
        cursor.execute("select idvolunteer from volunteer ")
        data = cursor.fetchall()
        data=list(data)
        for i in data:
            m =list(i)
        a=m[0]
        print(a)
        return HttpResponse("<script>alert('registered successfully  your volunteer id is "+str(a)+" but not approved yet. please wait while admins accept you as volunteer');window.location='../login';</script>")



def admin_home(request):
    return render(request,'admin_home.html')

def vol_home(request):
    volid = request.session['volid']
    return render(request,'vol_home.html',{'volid':volid})

def add_post(request):
    volid = request.session['volid']
    return render(request, 'vol_add_post.html',{'volid':volid})

def make_post(request):
    if request.method == "POST":
        details = request.POST['details']
        purpose = request.POST['purpose']
        amount = request.POST['amount']
        start = request.POST['start']
        end = request.POST['end']
        volid = request.session['volid']
        cursor = connection.cursor()
        cursor.execute("insert into donation_requirement values(null,'"+str(volid)+"','"+str(details)+"','trial',curdate() )")
        cursor.execute("select id_donation_requirement from donation_requirement where idvolunteer = '"+str(volid)+"' ")
        iddr = cursor.fetchall()
        iddr = list(iddr)
        for i in iddr:
            s =i[0]

        cursor.execute("insert into fund_raising values(null, '"+str(start)+"','"+str(end)+"','"+str(purpose)+"','0','"+str(amount)+"','"+str(s)+"' )")
        return redirect('vol_posts')
def vol_posts(request):
    volid = request.session['volid']
    cursor = connection.cursor()
    cursor.execute("select donation_requirement.*, fund_raising.* from donation_requirement join fund_raising where donation_requirement.idvolunteer ='"+str(volid)+"' and donation_requirement.id_donation_requirement = fund_raising.iddonation_requirement and donation_requirement.status ='trial' ")
    data = cursor.fetchall()
    cursor.execute("select donation_requirement.*, fund_raising.* from donation_requirement join fund_raising where donation_requirement.idvolunteer ='" + str(volid) + "' and donation_requirement.id_donation_requirement = fund_raising.iddonation_requirement and donation_requirement.status ='aborted' ")
    adata = cursor.fetchall()
    return render(request,'vol_posts.html',{'data':data,'adata':adata,'volid':volid})

def abort_post(request,id):
    cursor = connection.cursor()
    cursor.execute("update donation_requirement set status = 'aborted' where id_donation_requirement = '"+str(id)+"'")
    return redirect('vol_posts')

def activate_post(request,id):
    cursor = connection.cursor()
    cursor.execute("update donation_requirement set status = 'trial' where id_donation_requirement = '"+str(id)+"'")
    return redirect('vol_posts')

def user_home(request):
    uid = request.session['userid']
    return render(request,'user_home.html',{'uid':uid})

def view_posts(request):
    cursor = connection.cursor()
    cursor.execute("select donation_requirement.*, fund_raising.*,volunteer.charity from donation_requirement join fund_raising join volunteer where donation_requirement.id_donation_requirement = fund_raising.iddonation_requirement and donation_requirement.status = 'trial' and volunteer.idvolunteer = donation_requirement.idvolunteer ")

    data = cursor.fetchall()
    uid = request.session['userid']
    return render(request,'user_view_posts.html',{'data':data,'uid':uid})

def send_donation_request(request,id):
    uid = request.session['userid']
    cursor = connection.cursor()
    cursor.execute("select * from donation_response where iddonation_requirement = '"+str(id)+"' and userid ='"+str(uid)+"' and status ='pending' ")
    data = cursor.fetchone()
    if data == None:
        cursor.execute("select * from donation_response where iddonation_requirement = '" + str(id) + "' and userid ='" + str(uid) + "' and status ='accepted' ")
        data = cursor.fetchone()
        if data == None:
            return render(request,'user_send_donation_request.html',{'id':id,'uid':uid})
        else:
            return HttpResponse("<script>alert('you already send request for that post');window.location='../view_posts';</script>")
    else:
        return HttpResponse("<script>alert('you already send request for that post');window.location='../view_posts';</script>")



def send_donation_response(request):
    if request.method == "POST":
        uid = request.session['userid']
        id = request.POST['donation_requirement_id']
        details = request.POST['details']
        cursor = connection.cursor()
        cursor.execute("insert into donation_response values(null, '"+str(id)+"','"+str(details)+"','"+str(uid)+"','pending') ")
        return redirect('view_posts')

def approved_donation_requests(request):
    uid = request.session['userid']
    cursor = connection.cursor()
    cursor.execute("select * from donation_response where userid = '"+str(uid)+"' and status ='accepted'")
    data = cursor.fetchall()
    return render(request,'user_approved_donation_request.html',{'data':data,'uid':uid})

def payed_donation_requests(request):
    uid = request.session['userid']
    cursor = connection.cursor()
    cursor.execute("select * from donation_response where userid = '"+str(uid)+"' and status ='payed'")
    data = cursor.fetchall()
    return render(request,'user_payed_donation_request.html',{'data':data,'uid':uid})

def pending_donation_requests(request,id):
    volid = request.session['volid']
    cursor = connection.cursor()
    cursor.execute("select * from donation_response where status ='pending' and iddonation_requirement ='"+str(id)+"' ")
    data = cursor.fetchall()
    return render(request,'vol_pending_donation_request.html',{'data':data,'volid':volid})


def accept_donation_response(request, id):
    cursor = connection.cursor()
    cursor.execute("update donation_response set status = 'accepted' where id_donation_response = '"+str(id)+"' ")
    return redirect("vol_posts")



def accepted_donation_requests(request,id):
    volid = request.session['volid']
    cursor = connection.cursor()
    cursor.execute("select * from donation_response where status ='accepted' and iddonation_requirement ='" + str(id) + "' ")
    data = cursor.fetchall()
    connection.close()
    return render(request, 'vol_accepted_donation_request.html', {'data': data, 'volid': volid})

def vol_payed_donation_requests(request,id):
    volid = request.session['volid']
    cursor = connection.cursor()
    cursor.execute("select donation_response.*, transaction_history.* from donation_response join transaction_history where donation_response.status ='payed' and donation_response.iddonation_requirement ='" + str(id) + "' and donation_response.userid = transaction_history.user_id and donation_response.id_donation_response = transaction_history.iddonation_response")
    data = cursor.fetchall()
    connection.close()
    return render(request, 'vol_payed_donation_request.html', {'data': data, 'volid': volid})

def admin_vol_payed_donation_requests(request,id):
    cursor = connection.cursor()
    volid = request.session['avolid']
    cursor.execute("select donation_response.*, transaction_history.* from donation_response join transaction_history where donation_response.status ='payed' and donation_response.iddonation_requirement ='" + str(id) + "' and donation_response.userid = transaction_history.user_id and donation_response.id_donation_response = transaction_history.iddonation_response")
    data = cursor.fetchall()
    connection.close()
    return render(request, 'admin_vol_payed_donation_request.html', {'data': data,'volid':volid})

def admin_approved_volunteers(request):
    cursor = connection.cursor()
    cursor.execute("select * from volunteer where status ='approved'")
    data = cursor.fetchall()
    connection.close()
    return render(request,'admin_approved_volunteers.html',{'data':data})

def admin_view_vol_post(request,id):
    cursor = connection.cursor()
    cursor.execute("select donation_requirement.*, fund_raising.* from donation_requirement join fund_raising where donation_requirement.idvolunteer ='"+str(id)+"' and donation_requirement.id_donation_requirement = fund_raising.iddonation_requirement and donation_requirement.status ='trial' ")
    data = cursor.fetchall()
    cursor.execute("select donation_requirement.*, fund_raising.* from donation_requirement join fund_raising where donation_requirement.idvolunteer ='" + str(id) + "' and donation_requirement.id_donation_requirement = fund_raising.iddonation_requirement and donation_requirement.status ='aborted' ")
    adata = cursor.fetchall()
    request.session['avolid'] = id
    return render(request,'admin_view_vol_post.html',{'data':data,'adata':adata})


def admin_pending_volunteers(request):
    cursor = connection.cursor()
    cursor.execute("select * from volunteer where status ='pending'")
    data = cursor.fetchall()
    connection.close()
    return render(request, 'admin_pending_volunteers.html', {'data': data})

def admin_approve_volunteers(reauest,id):
    cursor = connection.cursor()
    cursor.execute("update volunteer set status ='approved' where idvolunteer ='"+str(id)+"'")
    return redirect('admin_pending_volunteers')


def vol_view_user_donation(request,jd,kd):
    volid = request.session['volid']
    cursor = connection.cursor()
    cursor.execute("select * from transaction_history where iddonation_response ='"+str(kd)+"' and iddonation_requirement = '"+str(jd)+"' ")
    data = cursor.fetchall()
    return render(request,'vol_view_user_donation.html',{'data':data,'volid':volid})

def user_view_donation(request,id,jd):
    uid = request.session['userid']
    cursor = connection.cursor()
    cursor.execute("select transaction_history.*, donation_requirement.details from transaction_history join donation_requirement where transaction_history.user_id ='"+str(uid)+"' and transaction_history.iddonation_requirement = '"+str(id)+"' and transaction_history.iddonation_response ='"+str(jd)+"' and transaction_history.iddonation_requirement = donation_requirement.id_donation_requirement ")
    data = cursor.fetchall()
    return render(request,'user_view_donation.html',{'data':data,'uid':uid})

def make_payment(request, id,res):
    uid = request.session['userid']
    if request.method == "POST":
        amount = request.POST['amount']
        cursor = connection.cursor()
        cursor.execute("select * from account_table ")
        v = cursor.fetchone()
        return render(request,'user_account_validate.html',{'id':id,'amount':amount,'row':v,'res':res})
    return render(request,'user_make_payment.html',{'uid':uid,'id':id})

def donate_items(request, id,res):
    uid = request.session['userid']
    cursor = connection.cursor()
    cursor.execute("select * from donations where user_id = '" + str(uid) + "' and iddonation_response ='" + str(res) + "' ")
    data = cursor.fetchone()
    if data == None:

        if request.method == "POST":
            item = request.POST['item_details']
            location = request.POST['location']
            cursor = connection.cursor()
            cursor.execute("insert into donations values(null, '"+str(uid)+"',curdate(), '"+str(item)+"','requested','"+str(id)+"','"+str(res)+"','"+str(location)+"') ")
            return HttpResponse("<script>alert('send donation item details for that post');window.location='../../../view_posts';</script>")

    else:
        return HttpResponse("<script>alert('you already send donation item details for that post');window.location='../../../view_posts';</script>")

    return render(request,'user_send_item_details.html',{'uid':uid,'id':id})

def requested_item_requests(request,id):
    volid = request.session['volid']
    cursor = connection.cursor()
    cursor.execute("select * from donations where iddonation_requirement ='" + str(id) + "' and status = 'requested' ")
    data = cursor.fetchall()
    return render(request, 'vol_view_requested_items.html', {'data': data, 'volid': volid})
def accept_donation_items(request,id):
    cursor = connection.cursor()
    cursor.execute("update donations set status ='collected' where iddonations ='"+str(id)+"' ")
    cursor.execute("select iddonation_response from donations where iddonations ='"+str(id)+"' ")
    data = cursor.fetchone()
    data = list(data)
    res =data[0]
    print(res)
    cursor.execute("updata donation_response set status = 'collected' where id_donation_response='"+str(res)+"' ")
    return redirect('vol_posts')


def accepted_item_requests(request,id):
    volid = request.session['volid']
    cursor = connection.cursor()
    cursor.execute("select * from donations where iddonation_requirement ='" + str(id) + "' and status = 'collected' ")
    data = cursor.fetchall()
    return render(request, 'vol_view_accepted_items.html', {'data': data, 'volid': volid})

def admin_accepted_item_requests(request,id):
    cursor = connection.cursor()
    volid =request.session['avolid']
    cursor.execute("select * from donations where iddonation_requirement ='" + str(id) + "' and status = 'collected' ")
    data = cursor.fetchall()
    return render(request, 'admin_vol_view_accepted_items.html', {'data': data, 'volid': volid})

def user_accepted_item_requests(request):
    uid = request.session['userid']
    cursor = connection.cursor()
    cursor.execute("select donations.*, donation_requirement.details from donations join donation_requirement where donations.user_id ='"+str(uid)+"' and donations.status ='collected' and donations.iddonation_requirement = donation_requirement.id_donation_requirement ")
    data = cursor.fetchall()
    return render(request,'user_accepted_item_request.html',{'data':data,'uid':uid})

def cancel_donation_item(request, id):

    cursor = connection.cursor()
    cursor.execute("delete from donations where iddonations ='"+str(id)+"' ")
    return redirect('user_accepted_item_requests')

def collected_item_requests(request,id):
    volid = request.session['volid']
    cursor = connection.cursor()
    cursor.execute("select * from donations where iddonation_requirement ='" + str(id) + "' and status = 'collected' ")
    data = cursor.fetchall()
    return render(request, 'vol_view_collected_items.html', {'data': data, 'volid': volid})




def validate_payment(request):
    uid = request.session['userid']
    if request.method == "POST":
        amount = request.POST['amount']
        id = request.POST['donationid']
        donres = request.POST['donres']
        card_no = request.POST['card_no']
        holder = request.POST['card_holder']
        exp = request.POST['card_expiry']
        cvv = request.POST['card_cvv']
        cursor = connection.cursor()
        cursor.execute("select * from account_table where card_number ='" + str(card_no) + "' and card_holder_name = '" + str(holder) + "' and  card_expiry_date= '" + str(exp) + "' and card_cvv = '" + str(cvv) + "' ")
        data = cursor.fetchone()
        if data ==None:
            return HttpResponse("<script>alert('Invalid  Card Entry ');window.location='approved_donation_requests';</script>")
        else:
            cursor.execute("insert into transaction_history values(null,'"+str(uid)+"', curdate(),'"+str(amount)+"', '"+str(id)+"','"+str(donres)+"')")
            cursor.execute("select collected_amount from fund_raising where iddonation_requirement = '"+str(id)+"' ")
            mata = cursor.fetchone()
            mata = list(mata)
            collected_amount =mata[0]

            print(collected_amount)

            collected_amount = int(collected_amount) + int(amount)

            cursor.execute("update fund_raising set collected_amount = '"+str(collected_amount)+"' where iddonation_requirement = '"+str(id)+"' ")
            cursor.execute("update donation_response set status = 'payed' where id_donation_response ='"+str(donres)+"'")
            cursor.execute("delete from donations where iddonation_response ='" + str(donres)+"'")
            return redirect('payed_donation_requests')

def user_send_feedback(request, id):
    uid = request.session['userid']
    return render(request,'user_send_feedback.html',{'id':id, 'uid':uid})
def send_feedback(request,id):
    cursor = connection.cursor()
    uid = request.session['userid']
    if request.method == "POST":
        feedback = request.POST['feedback']
        cursor.execute("insert into feedback values(null, '"+str(id)+"',curdate(),'"+str(feedback)+"','"+str(uid)+"')")
        connection.close()
        return redirect('user_view_feedback', id =id)

def user_view_feedback(request,id):
    cursor = connection.cursor()
    uid = request.session['userid']
    cursor.execute("select * from feedback where iddonations ='"+str(id)+"'")
    data = cursor.fetchall()
    return render(request,'user_view_feedback.html',{'data':data,'uid':uid})

def vol_view_feedback(request,id):
    cursor = connection.cursor()
    volid = request.session['volid']
    cursor.execute("select * from feedback where iddonations ='"+str(id)+"'")
    data = cursor.fetchall()
    return render(request,'vol_view_feedback.html',{'data':data,'volid':volid})

def admin_view_feedback(request,id):
    cursor = connection.cursor()
    volid = request.session['avolid']
    cursor.execute("select * from feedback where iddonations ='"+str(id)+"'")
    data = cursor.fetchall()
    return render(request,'admin_view_feedback.html',{'data':data,'volid':volid})

def add_money_spend(request):
    volid = request.session['volid']
    return render(request,'vol_add_money_spend.html',{'volid':volid})
def upload_money_spend(request):
    cursor = connection.cursor()
    volid = request.session['volid']
    if request.method == "POST":
        amount = request.POST['amount']
        details = request.POST['details']
        cursor.execute("insert into money_spend_details values(null,'"+str(details)+"',curdate(),'"+str(amount)+"','"+str(volid)+"')")
        connection.close()
        return redirect('vol_money_spends')

def vol_money_spends(request):
    cursor = connection.cursor()
    volid = request.session['volid']
    cursor.execute("select * from money_spend_details where volid ='" + str(volid) + "'")
    data = cursor.fetchall()
    return render(request, 'vol_view_money_spends.html', {'data': data, 'volid': volid})

def admin_view_money_spend(request,id):
    cursor = connection.cursor()
    cursor.execute("select * from money_spend_details where volid ='" + str(id) + "'")
    data = cursor.fetchall()
    return render(request, 'admin_view_money_spends.html',{'data': data})