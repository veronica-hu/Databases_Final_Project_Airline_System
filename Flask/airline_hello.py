from flask import Flask, render_template, request, session, url_for, redirect, flash
import pymysql

app = Flask(__name__)

conn = pymysql.connect(host='localhost',
                        user='root',
                        password='',
                        port=3307,   # only specialized for my server
                        db='Airline',  # temporary db
                        charset='utf8mb4')

@app.route('/')
def init():
    cursor = conn.cursor()
    query = "select a.airport_city as departure_city, departure_airport, departure_time, b.airport_city as arrival_city, arrival_airport, arrival_time, status\
            from flight, airport a, airport b\
            where flight.departure_airport=a.airport_name and flight.arrival_airport=b.airport_name and departure_time >= curdate()\
            order by departure_time;"
    cursor.execute(query)
    data1 = cursor.fetchall() 
    cursor.close()
    return render_template('init.html', posts=data1)

@app.route('/search', methods=['GET', 'POST'])
def init_search():
    cols1 = ['departure_city', 'departure_airport', 'arrival_city', 'arrival_airport', 'status']
    cols2 = ['departure_time', 'arrival_time']
    cursor = conn.cursor()
    query = "select * from\
            (select a.airport_city as departure_city, departure_airport, departure_time, b.airport_city as arrival_city, arrival_airport, arrival_time, status\
            from flight, airport a, airport b\
            where flight.departure_airport=a.airport_name and flight.arrival_airport=b.airport_name and departure_time >= curdate()\
            order by departure_time) temp"
    for c in cols1:
        v = request.form[c]
        if v != '':
            if query.endswith('temp'):
                query += " where"
                query += " temp.{}='{}'".format(c, v)
            else:
                query += " and temp.{}='{}'".format(c, v)
    for c in cols2:
        v = request.form[c]
        if v != '':
            if query.endswith('temp'):
                query += " where"
                query += " date(temp.{})='{}'".format(c, v)
            else:
                query += " and date(temp.{})='{}'".format(c, v)
    # print(query)
    query += " order by departure_time"
    cursor.execute(query)
    data1 = cursor.fetchall() 
    cursor.close()
    return render_template('init.html', posts=data1)

@app.route('/register/customer')
def register_customer():
    return render_template('register_customer.html')

@app.route('/register/agent')
def register_agent():
    return render_template('register_agent.html')

@app.route('/register/staff')
def register_staff():
    return render_template('register_staff.html')

@app.route('/registerAuth_customer', methods=['GET', 'POST'])
def registerAuth_customer():
    email = request.form['email']
    password = request.form['password']
    name = request.form['name']
    phone = request.form['phone']
    state = request.form['state']
    city = request.form['city']
    street = request.form['street']
    building = request.form['building']
    dob = request.form['dob']
    passport_country = request.form['passport_country']
    passport_number = request.form['passport_number']
    expiration_date = request.form['expiration_date']

    cursor = conn.cursor()
    query = "SELECT * FROM customer WHERE email = %s"
    cursor.execute(query, (email))
    data = cursor.fetchone()

    if(data):
        error = "This user already exists"
        return render_template('register_customer.html', error = error)
    else:
        ins = "INSERT INTO customer VALUES(%s, %s, md5(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(ins, (email, name, password, building, street, city, state, phone, passport_number,
                            expiration_date, passport_country, dob))
        conn.commit()
        cursor.close()
        flash("Registration Done.")
        return redirect(url_for('init'))

@app.route('/registerAuth_agent', methods=['GET', 'POST'])
def registerAuth_agent():
    email = request.form['email']
    password = request.form['password']
    id = request.form['agent ID']

    cursor = conn.cursor()
    query = "SELECT * FROM booking_agent WHERE email = %s"
    cursor.execute(query, (email))
    data = cursor.fetchone()

    if(data):
        error = "This user already exists"
        return render_template('register_agent.html', error = error)
    else:
        ins = "INSERT INTO booking_agent VALUES(%s, md5(%s), %s)"
        cursor.execute(ins, (email, password, id))
        conn.commit()
        cursor.close()
        flash("Registration Done.")
        return redirect(url_for('init'))

@app.route('/registerAuth_staff', methods=['GET', 'POST'])
def registerAuth_staff():
    username = request.form['username']
    password = request.form['password']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    dob = request.form['dob']
    airline = request.form['airline']

    cursor = conn.cursor()
    query = "SELECT * FROM airline_staff WHERE username = %s"
    cursor.execute(query, (username))
    data = cursor.fetchone()

    if(data):
        error = "This user already exists"
        return render_template('register_staff.html', error = error)
    else:
        ins = "INSERT INTO airline_staff VALUES(%s, md5(%s), %s, %s, %s, %s)"
        cursor.execute(ins, (username, password, first_name, last_name, dob, airline))
        conn.commit()
        cursor.close()
        flash("Registration Done.")
        return redirect(url_for('init'))
#-------------------------------------------------login----------------------------------------------------------
@app.route('/logout')
def logout():
    session.pop('username')
    session.pop('user')
    flash('You are logged out.')
    return redirect(url_for('init'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    user = request.form['user']
    username = request.form['username']
    password = request.form['password']

    cursor = conn.cursor()
    if user == 'customer':
        query = "SELECT * FROM customer WHERE email = %s and password = md5(%s)"
    elif user == 'agent':
        query = "SELECT * FROM booking_agent WHERE email = %s and password = md5(%s)"
    elif user == 'staff':
        query = "SELECT * FROM airline_staff WHERE username = %s and password = md5(%s)"
    
    cursor.execute(query, (username, password))
    data = cursor.fetchone()
    cursor.close()
	
    if(data):
        session['username'] = username
        session['user'] = user
        if user == 'staff':
            return redirect(url_for('staff_home'))
        elif user == 'agent':
            return redirect(url_for('agent_home'))
        elif user == 'customer':
            return redirect(url_for('customer_home'))

    else:
        flash('Invalid login or username.')
        return redirect(url_for('init'))
#---------------------------------------------customer-------------------------------------------------------
@app.route('/customer/home')
def customer_home():
    username = session['username']
    cursor = conn.cursor()
    query = "select distinct a.airport_city, departure_airport, departure_time, b.airport_city, arrival_airport, arrival_time, price, airline_name, airplane_id, flight_num, status\
    from flight join ticket using(flight_num, airline_name) join purchases using(ticket_id) join customer on(customer_email=customer.email) join airport a on (departure_airport=a.airport_name) join airport b on (arrival_airport=b.airport_name)\
    where customer.email=%s and departure_time >= curdate() order by departure_time;"
    cursor.execute(query, (username))
    data1 = cursor.fetchall()

    ## top 3 destinations in past 3-month and by 1 year
    query4 = "Select airport.airport_city, count(*)\
            from flight join airport on (flight.arrival_airport=airport.airport_name)\
            Where date_sub(curdate(), interval 3 month) <= flight.arrival_time and flight.arrival_time<=curdate()\
            Group by airport.airport_city Order by count(*) desc Limit 0, 3;"
    cursor.execute(query4)
    data4 = cursor.fetchall()

    query5 = "Select airport.airport_city, count(*)\
            from flight join airport on (flight.arrival_airport=airport.airport_name)\
            Where date_sub(curdate(), interval 1 year) <= flight.arrival_time and flight.arrival_time<=curdate()\
            Group by airport.airport_city Order by count(*) desc Limit 0, 3;"
    cursor.execute(query5)
    data5 = cursor.fetchall()
    cursor.close()

    context = {'data1':data1, 'data4':data4, 'data5':data5}
    cursor.close()
    return render_template('customer_home.html', username=username, **context)

@app.route('/customer/search', methods=['GET', 'POST'])
def customer_search():
    username = session['username']
    cols1 = ['departure_city', 'departure_airport', 'arrival_city', 'arrival_airport']
    cols2 = ['departure_time', 'arrival_time']
    cursor = conn.cursor()
    query = "select * from\
    (select distinct a.airport_city as departure_city, departure_airport, departure_time, b.airport_city as arrival_city, arrival_airport, arrival_time, price, airline_name, airplane_id, flight_num, status\
    from flight join ticket using(flight_num, airline_name) join purchases using(ticket_id) join customer on(customer_email=customer.email) join airport a on (departure_airport=a.airport_name) join airport b on (arrival_airport=b.airport_name)\
    where customer.email=%s and departure_time >= curdate()) temp"
    for c in cols1:
        v = request.form[c]
        if v != '':
            if query.endswith('temp'):
                query += " where"
                query += " temp.{}='{}'".format(c, v)
            else:
                query += " and temp.{}='{}'".format(c, v)
    for c in cols2:
        v = request.form[c]
        if v != '':
            if query.endswith('temp'):
                query += " where"
                query += " date(temp.{})='{}'".format(c, v)
            else:
                query += " and date(temp.{})='{}'".format(c, v)
    query += " order by departure_time"
    cursor.execute(query, (username))
    data1 = cursor.fetchall()

    ## top 3 destinations in past 3-month and by 1 year
    query4 = "Select airport.airport_city, count(*)\
            from flight join airport on (flight.arrival_airport=airport.airport_name)\
            Where date_sub(curdate(), interval 3 month) <= flight.arrival_time and flight.arrival_time<=curdate()\
            Group by airport.airport_city Order by count(*) desc Limit 0, 3;"
    cursor.execute(query4)
    data4 = cursor.fetchall()

    query5 = "Select airport.airport_city, count(*)\
            from flight join airport on (flight.arrival_airport=airport.airport_name)\
            Where date_sub(curdate(), interval 1 year) <= flight.arrival_time and flight.arrival_time<=curdate()\
            Group by airport.airport_city Order by count(*) desc Limit 0, 3;"
    cursor.execute(query5)
    data5 = cursor.fetchall()
    context = {'data1':data1, 'data4':data4, 'data5':data5}
    cursor.close()
    return render_template('customer_home.html', username=username, **context)

@app.route("/customer/purchase_ticket")
def customer_purchase_ticket():
    username = session['username']
    cursor = conn.cursor()
    query0 = "select distinct a.airport_city, departure_airport, departure_time, b.airport_city, arrival_airport, arrival_time, price, airline_name, airplane_id, flight_num, status\
    from flight join ticket using(flight_num, airline_name) join purchases using(ticket_id) join customer on(customer_email=customer.email) join airport a on (departure_airport=a.airport_name) join airport b on (arrival_airport=b.airport_name)\
    where customer.email=%s and departure_time >= curdate() order by departure_time;"
    cursor.execute(query0, (username))
    data0 = cursor.fetchall()

    query1 = "select airline_name, flight_num\
    from (select * from flight left join ticket using(airline_name, flight_num) where departure_time>=curdate()) a\
    group by airline_name, flight_num\
    having count(distinct ticket_id)< (select seats from airplane where airplane_id = a.airplane_id and airline_name=a.airline_name);"
    cursor.execute(query1)
    flights = cursor.fetchall()

    query2 = "select booking_agent_id from booking_agent"
    cursor.execute(query2)
    agent_id = cursor.fetchall()

    ## top 3 destinations in past 3-month and by 1 year
    query4 = "Select airport.airport_city, count(*)\
            from flight join airport on (flight.arrival_airport=airport.airport_name)\
            Where date_sub(curdate(), interval 3 month) <= flight.arrival_time and flight.arrival_time<=curdate()\
            Group by airport.airport_city Order by count(*) desc Limit 0, 3;"
    cursor.execute(query4)
    data4 = cursor.fetchall()
    query5 = "Select airport.airport_city, count(*)\
            from flight join airport on (flight.arrival_airport=airport.airport_name)\
            Where date_sub(curdate(), interval 1 year) <= flight.arrival_time and flight.arrival_time<=curdate()\
            Group by airport.airport_city Order by count(*) desc Limit 0, 3;"
    cursor.execute(query5)
    data5 = cursor.fetchall()
    cursor.close()
    context = {'data0':data0, 'agent_id':agent_id, 'flights':flights, 'data4':data4, 'data5':data5}
    return render_template('customer_purchase_ticket.html', username=username, **context)

@app.route("/customer/purchase_ticket/Auth", methods=['GET', 'POST'])
def customer_purchaseAuth():
    username = session['username']
    airline_name = request.form['flights'].split('-')[0]
    flight_num = request.form['flights'].split('-')[1]
    agent_id = request.form['agent_id']
    cursor = conn.cursor()
    # 暂时没有条件约束
    query1 = "insert into ticket (airline_name, flight_num) values (%s, %s);"
    cursor.execute(query1, (airline_name, flight_num))
    conn.commit()

    query2 = "select max(ticket_id) from ticket where airline_name=%s and flight_num=%s;"
    cursor.execute(query2, (airline_name, flight_num))
    ticket_id = cursor.fetchall()

    import datetime
    purchase_date = datetime.datetime.now().strftime("%Y-%m-%d")

    if agent_id == '':
        query4 = "insert into purchases values (%s, %s, null, %s);"
        cursor.execute(query4, (ticket_id, username, purchase_date))
        conn.commit()
    else:
        query4 = "insert into purchases values (%s, %s, %s, %s);"
        cursor.execute(query4, (ticket_id, username, agent_id, purchase_date))
        conn.commit()
    cursor.close()
    flash("Ticket Purchased.")
    return redirect(url_for('customer_purchase_ticket'))

@app.route("/customer/track_spending")
def customer_track_spending():
    username = session['username']
    cursor = conn.cursor()
    # total spending in past year
    query0 = "select sum(price)\
    from flight join ticket using(airline_name, flight_num) join purchases using(ticket_id)\
    where customer_email = %s and date_sub(curdate(), interval 1 year)<= purchase_date;"
    cursor.execute(query0, (username))
    data0 = cursor.fetchone()

    # monthly spending in past 6 month
    query1 = "select month(purchase_date), sum(price)\
    from flight join ticket using(airline_name, flight_num) join purchases using(ticket_id)\
    where customer_email = %s and date_sub(curdate(), interval 6 month)<= purchase_date\
    group by month(purchase_date);"
    cursor.execute(query1, (username))
    data1 = cursor.fetchall()

    # for data2 and data3, since the user hasn't specify a date range, we first show empty values
    context = {'data0':data0, 'data1':data1, 'data2':[''], 'data3':['']}

    # direct to the web page
    return render_template('track_spending.html', username=username, **context)

@app.route("/customer/spending_time", methods=['GET', 'POST'])
def customer_spending_time():
    username = session['username']
    cursor = conn.cursor()
    query0 = "select sum(price)\
    from flight join ticket using(airline_name, flight_num) join purchases using(ticket_id)\
    where customer_email = %s and date_sub(curdate(), interval 1 year)<= purchase_date;"
    cursor.execute(query0, (username))
    data0 = cursor.fetchone()
    query1 = "select month(purchase_date), sum(price)\
    from flight join ticket using(airline_name, flight_num) join purchases using(ticket_id)\
    where customer_email = %s and date_sub(curdate(), interval 6 month)<= purchase_date\
    group by month(purchase_date);"
    cursor.execute(query1, (username))
    data1 = cursor.fetchall()

    # now use request.form to grab user-defined date range
    # search for total spending in the date range
    from_date = request.form['from_date']
    to_date = request.form['to_date']
    query2 = "select sum(price)\
    from flight join ticket using(airline_name, flight_num) join purchases using(ticket_id)\
    where customer_email = %s and purchase_date between %s and %s"
    cursor.execute(query2, (username, from_date, to_date))
    data2 = cursor.fetchone()

    # search for monthly spending in date range
    query3 = "select month(purchase_date), sum(price)\
    from flight join ticket using(airline_name, flight_num) join purchases using(ticket_id)\
    where customer_email = %s and purchase_date between %s and %s group by month(purchase_date);"
    cursor.execute(query3, (username, from_date, to_date))
    data3 = cursor.fetchall()

    # store new data into context
    context = {'data0':data0, 'data1':data1, 'data2':data2, 'data3':data3}

    # direct to the same html page with newly selected data
    return render_template('track_spending.html', username=username, **context)
#---------------------------------------------booking agent--------------------------------------------------
@app.route('/agent/home')
def agent_home():
    username = session['username']
    cursor = conn.cursor()
    query = "select distinct a.airport_city, departure_airport, departure_time, b.airport_city, arrival_airport, arrival_time, price, airline_name, airplane_id, flight_num, status\
    from flight join ticket using(flight_num, airline_name) join purchases using(ticket_id) join booking_agent using(booking_agent_id) join airport a on (departure_airport=a.airport_name) join airport b on (arrival_airport=b.airport_name)\
    where booking_agent.email=%s and departure_time >= curdate() order by departure_time;"
    cursor.execute(query, (username))
    data = cursor.fetchall() 
    cursor.close()
    return render_template('agent_home.html', username=username, posts=data)

@app.route('/agent/search', methods=['GET', 'POST'])
def agent_search():
    username = session['username']
    cols1 = ['departure_city', 'departure_airport', 'arrival_city', 'arrival_airport']
    cols2 = ['departure_time', 'arrival_time']
    cursor = conn.cursor()
    query = "select * from\
        (select distinct a.airport_city as departure_city, departure_airport, departure_time, b.airport_city as arrival_city, arrival_airport, arrival_time, price, airline_name, airplane_id, flight_num, status\
    from flight join ticket using(flight_num, airline_name) join purchases using(ticket_id) join booking_agent using(booking_agent_id) join airport a on (departure_airport=a.airport_name) join airport b on (arrival_airport=b.airport_name)\
    where booking_agent.email=%s and departure_time >= curdate()) temp"
    for c in cols1:
        v = request.form[c]
        if v != '':
            if query.endswith('temp'):
                query += " where"
                query += " temp.{}='{}'".format(c, v)
            else:
                query += " and temp.{}='{}'".format(c, v)
    for c in cols2:
        v = request.form[c]
        if v != '':
            if query.endswith('temp'):
                query += " where"
                query += " date(temp.{})='{}'".format(c, v)
            else:
                query += " and date(temp.{})='{}'".format(c, v)
    query += " order by departure_time"
    cursor.execute(query, (username))
    data = cursor.fetchall() 
    cursor.close()
    return render_template('agent_home.html', username=username, posts=data)

@app.route("/agent/purchase_ticket")
def agent_purchase_ticket():
    username = session['username']
    cursor = conn.cursor()
    query0 = "select distinct a.airport_city, departure_airport, departure_time, b.airport_city, arrival_airport, arrival_time, price, airline_name, airplane_id, flight_num, status\
    from flight join ticket using(flight_num, airline_name) join purchases using(ticket_id) join booking_agent using(booking_agent_id) join airport a on (departure_airport=a.airport_name) join airport b on (arrival_airport=b.airport_name)\
    where booking_agent.email=%s and departure_time >= curdate() order by departure_time;"
    cursor.execute(query0, (username))
    data0 = cursor.fetchall()

    query1 = "select email from customer"
    cursor.execute(query1)
    customers = cursor.fetchall() 
    query2 = "select airline_name, flight_num\
    from (select * from flight left join ticket using(airline_name, flight_num) where departure_time>=curdate()) a\
    group by airline_name, flight_num\
    having count(distinct ticket_id)< (select seats from airplane where airplane_id = a.airplane_id and airline_name=a.airline_name);"
    cursor.execute(query2)
    flights = cursor.fetchall()

    cursor.close()
    context = {'data0':data0, 'customers':customers, 'flights':flights}
    return render_template('agent_purchase_ticket.html', username=username, **context)

@app.route("/agent/purchase_ticket/Auth", methods=['GET', 'POST'])
def agent_purchaseAuth():
    username = session['username']
    customer_email = request.form['customer_email']
    airline_name = request.form['flights'].split('-')[0]
    flight_num = request.form['flights'].split('-')[1]

    cursor = conn.cursor()
    # 暂时没有条件约束
    query1 = "insert into ticket (airline_name, flight_num) values (%s, %s);"
    cursor.execute(query1, (airline_name, flight_num))
    conn.commit()

    query2 = "select max(ticket_id) from ticket where airline_name=%s and flight_num=%s;"
    cursor.execute(query2, (airline_name, flight_num))
    ticket_id = cursor.fetchall()

    query3 = "select booking_agent_id from booking_agent where email=%s;"
    cursor.execute(query3, (username))
    booking_agent_id = cursor.fetchall()

    import datetime
    purchase_date = datetime.datetime.now().strftime("%Y-%m-%d")

    query4 = "insert into purchases values (%s, %s, %s, %s);"
    cursor.execute(query4, (ticket_id, customer_email, booking_agent_id, purchase_date))
    conn.commit()

    cursor.close()
    flash("Ticket Purchased.")
    return redirect(url_for('agent_purchase_ticket'))

@app.route('/agent/view_commission')
def view_commission():
    username = session['username']
    cursor = conn.cursor()
    query0 = "select distinct a.airport_city, departure_airport, departure_time, b.airport_city, arrival_airport, arrival_time, price, airline_name, airplane_id, flight_num, status\
    from flight join ticket using(flight_num, airline_name) join purchases using(ticket_id) join booking_agent using(booking_agent_id) join airport a on (departure_airport=a.airport_name) join airport b on (arrival_airport=b.airport_name)\
    where booking_agent.email=%s and departure_time >= curdate() order by departure_time;"
    cursor.execute(query0, (username))
    data0 = cursor.fetchall() 

    # total commission in past 30 days
    query1 = "Select round(sum(0.1*price),2) as total_commission\
    From flight join ticket using(flight_num, airline_name) join purchases using(ticket_id) join booking_agent using(booking_agent_id)\
    Where booking_agent.email = %s and date_sub(curdate(), interval 30 day) <= purchase_date;"
    cursor.execute(query1, (username))
    data1 = cursor.fetchone() 

    # average commission in past 30 days
    query2 = "Select round(avg(0.1*price),2) as average_commission\
    From flight join ticket using(flight_num, airline_name) join purchases using(ticket_id) join booking_agent using(booking_agent_id)\
    Where booking_agent.email = %s and date_sub(curdate(), interval 30 day) <= purchase_date;"
    cursor.execute(query2, (username))
    data2 = cursor.fetchone() 

    # number of tickets sold in past 30 days
    query3 = "Select count(ticket_id)\
    From ticket join purchases using(ticket_id) join booking_agent using(booking_agent_id)\
    Where booking_agent.email = %s and date_sub(curdate(), interval 30 day) <= purchase_date;"
    cursor.execute(query3, (username))
    data3 = cursor.fetchone() 
    cursor.close()

    context = {'data0':data0, 'data1':data1, 'data2':data2, 'data3':data3, 'data5':[''], 'data4':['']}
    return render_template('view_commission.html', username=username, **context)

@app.route("/agent/view_Commission/Auth", methods=['GET', 'POST'])
def view_commissionAuth():
    username = session['username']
    cursor = conn.cursor()
    query0 = "select distinct a.airport_city, departure_airport, departure_time, b.airport_city, arrival_airport, arrival_time, price, airline_name, airplane_id, flight_num, status\
    from flight join ticket using(flight_num, airline_name) join purchases using(ticket_id) join booking_agent using(booking_agent_id) join airport a on (departure_airport=a.airport_name) join airport b on (arrival_airport=b.airport_name)\
    where booking_agent.email=%s and departure_time >= curdate() order by departure_time;"
    cursor.execute(query0, (username))
    data0 = cursor.fetchall() 
    query1 = "Select round(sum(0.1*price),2) as total_commission\
    From flight join ticket using(flight_num, airline_name) join purchases using(ticket_id) join booking_agent using(booking_agent_id)\
    Where booking_agent.email = %s and date_sub(curdate(), interval 30 day) <= purchase_date;"
    cursor.execute(query1, (username))
    data1 = cursor.fetchone() 
    query2 = "Select round(avg(0.1*price),2) as average_commission\
    From flight join ticket using(flight_num, airline_name) join purchases using(ticket_id) join booking_agent using(booking_agent_id)\
    Where booking_agent.email = %s and date_sub(curdate(), interval 30 day) <= purchase_date;"
    cursor.execute(query2, (username))
    data2 = cursor.fetchone() 
    query3 = "Select count(ticket_id)\
    From ticket join purchases using(ticket_id) join booking_agent using(booking_agent_id)\
    Where booking_agent.email = %s and date_sub(curdate(), interval 30 day) <= purchase_date;"
    cursor.execute(query3, (username))
    data3 = cursor.fetchone() 

    from_date = request.form['from_date']
    to_date = request.form['to_date']
    query4 = "Select round(sum(0.1*price),2) as total_commission\
    From flight join ticket using(flight_num, airline_name) join purchases using(ticket_id) join booking_agent using(booking_agent_id)\
    Where booking_agent.email = %s and purchase_date between %s and %s;"
    cursor.execute(query4, (username, from_date, to_date))
    data4 = cursor.fetchone()
    query5 = "Select count(ticket_id)\
    From ticket join purchases using(ticket_id) join booking_agent using(booking_agent_id)\
    Where booking_agent.email = %s and purchase_date between %s and %s;"
    cursor.execute(query5, (username, from_date, to_date))
    data5 = cursor.fetchone()
    cursor.close()

    context = {'data0':data0, 'data1':data1, 'data2':data2, 'data3':data3, 'data5':data5, 'data4':data4}
    return render_template('view_commission.html', username=username, **context)

@app.route("/agent/view_customer")
def agent_view_customer():
    username = session['username']
    cursor = conn.cursor()
    # top 5 customers based on # of tickets in 6 months
    query1 = "Select customer_email, count(ticket_id) as count\
    From purchases join booking_agent using(booking_agent_id)\
    Where booking_agent.email = %s and date_sub(curdate(), interval 6 month) <= purchase_date\
    Group by customer_email order by count desc Limit 0, 5;"
    cursor.execute(query1, (username))
    data1 = cursor.fetchall()

    query2 = "Select customer_email, sum(0.1*price) as total\
    From ticket join flight using(flight_num, airline_name) join purchases using(ticket_id) join booking_agent using(booking_agent_id)\
    Where booking_agent.email = %s and date_sub(curdate(), interval 1 year) <= purchase_date\
    Group by customer_email order by total desc Limit 0, 5;"
    cursor.execute(query2, (username))
    data2 = cursor.fetchall()
    cursor.close()

    context = {'data1':data1, 'data2':data2}
    return render_template('agent_view_customer.html', username=username, **context)
#---------------------------------------------airline staff--------------------------------------------------
@app.route('/staff/home')
def staff_home():
    username = session['username']
    if session['user']  != 'staff':
        flash('Unauthorized User. Please login in as the correct user type.')
        return redirect(url_for('init'))

    cursor = conn.cursor()
    query1 = "select distinct a.airport_city, departure_airport, departure_time, b.airport_city,  arrival_airport, arrival_time, price, airline_name, airplane_id, flight_num, status\
    from airline_staff join flight using(airline_name) join airport a on (departure_airport=a.airport_name) join airport b on (arrival_airport=b.airport_name)\
    where airline_staff.username=%s and date_sub(curdate(), interval 1 month)<=departure_time and departure_time >= curdate()\
    order by departure_time limit 0,5;"
    cursor.execute(query1, (username))
    data1 = cursor.fetchall() 

    ## top 5 agents based on monthly # of sold tickets
    query2 = "select email, count(*)\
            from ticket join purchases using (ticket_id) join booking_agent using(booking_agent_id) join airline_staff using(airline_name)\
            where airline_staff.username=%s and date_sub(curdate(), interval 1 month)<=purchase_date\
            group by email order by count(*) desc limit 0, 5;"
    cursor.execute(query2, (username))
    data2 = cursor.fetchall()

    ## top 5 frequent customers (for the particular airline only)
    query3 = "Select customer_email, count(*)\
            from purchases join ticket using (ticket_id) join airline_staff using(airline_name)\
            Where airline_staff.username = %s and date_sub(curdate(), interval 1 year)<=purchase_date\
            Group by customer_email Order by count(*) desc Limit 0, 5;"
    cursor.execute(query3, (username))
    data3 = cursor.fetchall()

    ## top 3 destinations in past 3-month and by 1 year
    query4 = "Select airport.airport_city, count(*)\
            from airline_staff join flight using(airline_name) join airport on (flight.arrival_airport=airport.airport_name)\
            Where airline_staff.username =%s and date_sub(curdate(), interval 3 month) <= flight.arrival_time and flight.arrival_time<=curdate()\
            Group by airport.airport_city Order by count(*) desc Limit 0, 3;"
    cursor.execute(query4, (username))
    data4 = cursor.fetchall()

    query5 = "Select airport.airport_city, count(*)\
            from airline_staff join flight using(airline_name) join airport on (flight.arrival_airport=airport.airport_name)\
            Where airline_staff.username =%s and date_sub(curdate(), interval 1 year) <= flight.arrival_time and flight.arrival_time<=curdate()\
            Group by airport.airport_city Order by count(*) desc Limit 0, 3;"
    cursor.execute(query5, (username))
    data5 = cursor.fetchall()
    cursor.close()

    context = {'data1':data1, 'data2':data2, 'data3':data3, 'data4':data4, 'data5':data5}
    return render_template('staff_home.html', username=username, **context)

@app.route('/staff/view_flight')
def view_flight():
    username = session['username']
    if session['user']  != 'staff':
        flash('Unauthorized User. Please login in as the correct user type.')
        return redirect(url_for('init'))
    cursor = conn.cursor()
    # default: upcoming flights in 30 days
    query = "select distinct a.airport_city, departure_airport, departure_time, b.airport_city,  arrival_airport, arrival_time, price, airline_name, airplane_id, flight_num, status\
    from airline_staff join flight using(airline_name) join airport a on (departure_airport=a.airport_name) join airport b on (arrival_airport=b.airport_name)\
    where airline_staff.username=%s and date_sub(curdate(), interval 1 month)<=departure_time and departure_time >= curdate()\
    order by departure_time;"
    cursor.execute(query, (username))
    data1 = cursor.fetchall() 
    cursor.close()
    return render_template('staff_flight.html', username=username, posts=data1)

@app.route('/staff/search', methods=['GET', 'POST'])
def staff_search():
    username = session['username']
    if session['user']  != 'staff':
        flash('Unauthorized User. Please login in as the correct user type.')
        return redirect(url_for('init'))
    cursor = conn.cursor()
    cols1 = ['departure_city', 'departure_airport', 'arrival_city', 'arrival_airport', 'flight_num', 'status']
    # search for all flights of the airline he/she works for 
    query = "select * from \
    (select distinct a.airport_city as departure_city, departure_airport, departure_time, b.airport_city as arrival_city,  arrival_airport, arrival_time, price, airline_name, airplane_id, flight_num, status\
    from airline_staff join flight using(airline_name) join airport a on (departure_airport=a.airport_name) join airport b on (arrival_airport=b.airport_name)\
    where airline_staff.username=%s order by departure_time) temp"
    for c in cols1:
        v = request.form[c]
        if v != '':
            if query.endswith('temp'):
                query += " where"
                query += " temp.{}='{}'".format(c, v)
            else: 
                query += " and temp.{}='{}'".format(c, v)
    departure_from = request.form['departure_from']
    departure_to = request.form['departure_to']
    arrival_from = request.form['arrival_from']
    arrival_to = request.form['arrival_to']
    price_from = request.form['price_from']
    price_to = request.form['price_to']
    if departure_from != '':
        if query.endswith('temp'):
            query += " where"
            query += " date(temp.departure_time)>='{}'".format(departure_from)
        else:
            query += " and date(temp.departure_time)>='{}'".format(departure_from)
    if arrival_from != '':
        if query.endswith('temp'):
            query += " where"
            query += " date(temp.arrival_time)>='{}'".format(arrival_from)
        else:
            query += " and date(temp.arrival_time)>='{}'".format(arrival_from)
    if departure_to != '':
        if query.endswith('temp'):
            query += " where"
            query += " date(temp.departure_time)<='{}'".format(departure_to)
        else:
            query += " and date(temp.departure_time)<='{}'".format(departure_to)
    if arrival_to != '':
        if query.endswith('temp'):
            query += " where"
            query += " date(temp.arrival_time)<='{}'".format(arrival_to)
        else:
            query += " and date(temp.arrival_time)<='{}'".format(arrival_to)
    if price_from != '':
        if query.endswith('temp'):
            query += " where"
            query += " price>='{}'".format(price_from)
        else:
            query += " and price>='{}'".format(price_from)
    if price_to != '':
        if query.endswith('temp'):
            query += " where"
            query += " price<='{}'".format(price_to)
        else:
            query += " and price<='{}'".format(price_to)

    query += ' order by departure_time'
    cursor = conn.cursor()
    cursor.execute(query, (username))
    data = cursor.fetchall()
    cursor.close()
    return render_template('staff_flight.html', username=username, posts=data)

@app.route('/staff/create_flight')
def create_flight():
    username = session['username']
    if session['user']  != 'staff':
        flash('Unauthorized User. Please login in as the correct user type.')
        return redirect(url_for('init'))
    cursor = conn.cursor()
    query1 = "select distinct a.airport_city, departure_airport, departure_time, b.airport_city,  arrival_airport, arrival_time, price, airline_name, airplane_id, flight_num, status\
    from airline_staff join flight using(airline_name) join airport a on (departure_airport=a.airport_name) join airport b on (arrival_airport=b.airport_name)\
    where airline_staff.username=%s and date_sub(curdate(), interval 1 month)<=departure_time and departure_time >= curdate()\
    order by departure_time;"
    cursor.execute(query1, (username))
    data1 = cursor.fetchall() 

    query2 = "select airport_name from airport"
    cursor.execute(query2)
    airports = cursor.fetchall() 

    query3 = "select airline_name from airline_staff where username=%s"
    cursor.execute(query3, (username))
    airline = cursor.fetchone() 

    query4 = "select airplane_id from airplane join airline_staff using(airline_name) where username=%s"
    cursor.execute(query4, (username))
    airplanes = cursor.fetchall() 
    cursor.close()

    context={'data1':data1, 'airports':airports, 'airline':airline, 'airplanes':airplanes}
    return render_template('create_flight.html', username=username, **context)

@app.route('/staff/create_flight/Auth', methods=['GET', 'POST'])
def create_flightAuth():
    username = session['username']
    if session['user']  != 'staff':
        flash('Unauthorized User. Please login in as the correct user type.')
        return redirect(url_for('init'))
    departure_airport = request.form['departure_airport']
    departure_time = request.form['departure_date']+' '+request.form['departure_time']
    arrival_airport = request.form['arrival_airport']
    arrival_time = request.form['arrival_date']+' '+request.form['arrival_time']
    price = request.form['price']
    id = request.form['id']
    flight_num = request.form['flight_num']
    status = request.form['status']

    cursor = conn.cursor()
    query0 = "select airline_name from airline_staff where username=%s"
    cursor.execute(query0, (username))
    airline = cursor.fetchone() 

    query1 = "SELECT * FROM flight WHERE airline_name=%s and flight_num = %s"
    cursor.execute(query1, (airline, flight_num))
    data1 = cursor.fetchone()
    if(data1):
        flash("This flight already exists.")
        return redirect(url_for('create_flight'))
    else:
        ins = "INSERT INTO flight VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(ins, (airline,flight_num,departure_airport,departure_time,arrival_airport,arrival_time,price,status,id))
        conn.commit()
        cursor.close()
        flash("Flight Created.")
        return redirect(url_for('create_flight'))

@app.route('/staff/change_status')
def change_status():
    username = session['username']
    if session['user']  != 'staff':
        flash('Unauthorized User. Please login in as the correct user type.')
        return redirect(url_for('init'))
    cursor = conn.cursor()
    query1 = "select distinct a.airport_city, departure_airport, departure_time, b.airport_city,  arrival_airport, arrival_time, price, airline_name, airplane_id, flight_num, status\
    from airline_staff join flight using(airline_name) join airport a on (departure_airport=a.airport_name) join airport b on (arrival_airport=b.airport_name)\
    where airline_staff.username=%s and date_sub(curdate(), interval 1 month)<=departure_time and departure_time >= curdate()\
    order by departure_time;"
    cursor.execute(query1, (username))
    data1 = cursor.fetchall() 

    query2 = "select airline_name from airline_staff where username=%s"
    cursor.execute(query2, (username))
    airline = cursor.fetchone() 

    query3 = "select flight_num from flight where airline_name=%s and departure_time>=curdate()"
    cursor.execute(query3, (airline))
    flight_nums = cursor.fetchall() 
    cursor.close()

    context={'data1':data1, 'airline':airline, 'flight_nums':flight_nums}
    return render_template('change_status.html', username=username, **context)

@app.route('/staff/change_status/Auth', methods=['GET', 'POST'])
def change_statusAuth():
    username = session['username']
    cursor = conn.cursor()
    query0 = "select airline_name from airline_staff where username=%s"
    cursor.execute(query0, (username))
    airline = cursor.fetchone() 

    flight_num = request.form['flight_num']
    status = request.form['status']

    # 暂时没有条件约束
    query1 = "update flight set status=%s where airline_name=%s and flight_num=%s"
    cursor.execute(query1, (status, airline, flight_num))
    conn.commit()
    cursor.close()
    flash("Status Changed.")
    return redirect(url_for('change_status'))

@app.route('/staff/add_airplane')
def add_airplane():
    username = session['username']
    if session['user']  != 'staff':
        flash('Unauthorized User. Please login in as the correct user type.')
        return redirect(url_for('init'))
    cursor = conn.cursor()
    query1 = "select distinct a.airport_city, departure_airport, departure_time, b.airport_city,  arrival_airport, arrival_time, price, airline_name, airplane_id, flight_num, status\
    from airline_staff join flight using(airline_name) join airport a on (departure_airport=a.airport_name) join airport b on (arrival_airport=b.airport_name)\
    where airline_staff.username=%s and date_sub(curdate(), interval 1 month)<=departure_time and departure_time >= curdate()\
    order by departure_time;"
    cursor.execute(query1, (username))
    data1 = cursor.fetchall() 

    query2 = "select airline_name from airline_staff where username=%s"
    cursor.execute(query2, (username))
    airline = cursor.fetchone() 

    query3 = "select airplane_id from airplane join airline_staff using(airline_name) where username=%s"
    cursor.execute(query3, (username))
    airplanes = cursor.fetchall() 
    cursor.close()

    context={'data1':data1, 'airline':airline, 'airplanes':airplanes}
    return render_template('add_airplane.html', username=username, **context)

@app.route('/staff/add_airplane/Auth', methods=['GET', 'POST'])
def add_airplaneAuth():
    username = session['username']
    id = request.form['id']
    seats = request.form['seats']

    cursor = conn.cursor()
    query0 = "select airline_name from airline_staff where username=%s"
    cursor.execute(query0, (username))
    airline = cursor.fetchone() 

    query1 = "SELECT * FROM airplane WHERE airline_name=%s and airplane_id = %s"
    cursor.execute(query1, (airline, id))
    data1 = cursor.fetchone()
    if(data1):
        flash("This airplane already exists.")
        return redirect(url_for('add_airplane'))
    else:
        ins = "INSERT INTO airplane VALUES(%s, %s, %s)"
        cursor.execute(ins, (airline, id, seats))
        conn.commit()
        cursor.close()
        flash("Airplane Added.")
        return redirect(url_for('add_airplane'))

@app.route('/staff/add_airport')
def add_airport():
    username = session['username']
    if session['user']  != 'staff':
        flash('Unauthorized User. Please login in as the correct user type.')
        return redirect(url_for('init'))
    cursor = conn.cursor()
    query1 = "select distinct a.airport_city, departure_airport, departure_time, b.airport_city,  arrival_airport, arrival_time, price, airline_name, airplane_id, flight_num, status\
    from airline_staff join flight using(airline_name) join airport a on (departure_airport=a.airport_name) join airport b on (arrival_airport=b.airport_name)\
    where airline_staff.username=%s and date_sub(curdate(), interval 1 month)<=departure_time and departure_time >= curdate()\
    order by departure_time;"
    cursor.execute(query1, (username))
    data1 = cursor.fetchall() 

    query2 = "select airport_name from airport"
    cursor.execute(query2)
    airports = cursor.fetchall() 
    cursor.close()

    context={'data1':data1, 'airports':airports}
    return render_template('add_airport.html', username=username, **context)

@app.route('/staff/add_airport/Auth', methods=['GET', 'POST'])
def add_airportAuth():
    username = session['username']
    name = request.form['name']
    city = request.form['city']
    cursor = conn.cursor()
    query = "select * from airport where airport_name=%s"
    cursor.execute(query, (name))
    data = cursor.fetchone()
    if(data):
        flash("This airport already exists.")
        return redirect(url_for('add_airport'))
    else:
        ins = "INSERT INTO airport VALUES(%s, %s)"
        cursor.execute(ins, (name, city))
        conn.commit()
        cursor.close()
        flash("Airport Added.")
        return redirect(url_for('add_airport'))

@app.route('/staff/view_customer')
def view_customer():
    username = session['username']
    if session['user']  != 'staff':
        flash('Unauthorized User. Please login in as the correct user type.')
        return redirect(url_for('init'))
    cursor = conn.cursor()
    query1 = "select distinct a.airport_city, departure_airport, departure_time, b.airport_city,  arrival_airport, arrival_time, price, airline_name, airplane_id, flight_num, status\
    from airline_staff join flight using(airline_name) join airport a on (departure_airport=a.airport_name) join airport b on (arrival_airport=b.airport_name)\
    where airline_staff.username=%s and date_sub(curdate(), interval 1 month)<=departure_time and departure_time >= curdate()\
    order by departure_time;"
    cursor.execute(query1, (username))
    data1 = cursor.fetchall() 

    query2 = "select airline_name from airline_staff where username=%s"
    cursor.execute(query2, (username))
    airline = cursor.fetchone() 

    query3 = "select flight_num from flight where airline_name=%s" # and departure_time>=curdate()
    cursor.execute(query3, (airline))
    flight_nums = cursor.fetchall() 
    cursor.close()

    context={'data1':data1, 'airline':airline, 'flight_nums':flight_nums}
    return render_template('staff_customer.html', username=username, **context)

@app.route('/staff/view_customer_results', methods=['GET', 'POST'])
def view_customer_results():
    username = session['username']
    cursor = conn.cursor()
    query0 = "select airline_name from airline_staff where username=%s"
    cursor.execute(query0, (username))
    airline = cursor.fetchone() 
    cursor.close()
    flight_num = request.form['flight_num']

    cursor = conn.cursor()
    query1 = "Select email, airline_name, flight_num, ticket_id, departure_time, departure_airport, arrival_time, arrival_airport, booking_agent_id\
            From flight join ticket using (flight_num, airline_name) join purchases using(ticket_id) join customer on(purchases.customer_email=customer.email)\
            where flight.airline_name =%s and flight.flight_num = %s;"
    cursor.execute(query1, (airline, flight_num))
    data = cursor.fetchall()
    cursor.close()
    return render_template('staff_customer_results.html', username=username, posts=data)

@app.route('/staff/top_agents')
def top_agents():
    username = session['username']
    ## top 5 agents based on monthly # of sold tickets
    cursor = conn.cursor()
    query1 = "select email, count(*)\
            from ticket join purchases using (ticket_id) join booking_agent using(booking_agent_id) join airline_staff using(airline_name)\
            where airline_staff.username=%s and date_sub(curdate(), interval 1 month)<=purchase_date\
            group by email order by count(*) desc limit 0, 5;"
    cursor.execute(query1, (username))
    data1 = cursor.fetchall()

    ## top 5 agents based on yearly # of sold tickets
    query2 = "select email, count(*)\
            from ticket join purchases using (ticket_id) join booking_agent using(booking_agent_id) join airline_staff using(airline_name)\
            where airline_staff.username=%s and date_sub(curdate(), interval 1 year)<=purchase_date\
            group by email order by count(*) desc limit 0, 5;"
    cursor.execute(query2, (username))
    data2 = cursor.fetchall()

    ## top 5 agents based on yearly commission
    query3 = "select email, sum(price*0.1) as commission\
            from ticket join flight using (flight_num, airline_name) join purchases using(ticket_id) join booking_agent using(booking_agent_id) join airline_staff using(airline_name)\
            where airline_staff.username=%s and date_sub(curdate(), interval 1 year)<=purchase_date\
            group by email order by commission DESC limit 0, 5;"
    cursor.execute(query3, (username))
    data3 = cursor.fetchall()
    cursor.close()

    context={'data1':data1, 'data2':data2,'data3':data3}
    return render_template('top_agents.html', username=username, **context)

@app.route('/staff/reports')
def staff_reports():
    username = session['username']

    # number of tickets sold in 1 year (specify airline)
    cursor = conn.cursor()
    query1 = "Select count(distinct ticket_id)\
            From ticket join purchases using (ticket_id) join airline_staff using (airline_name)\
            Where airline_staff.username = %s and date_sub(curdate(), interval 1 year)<=purchase_date"
    cursor.execute(query1, (username))
    data1 = cursor.fetchone()

    # number of tickets sold in 1 month
    query2 = "Select count(distinct ticket_id)\
            From ticket join purchases using (ticket_id) join airline_staff using (airline_name)\
            Where airline_staff.username = %s and date_sub(curdate(), interval 1 month)<=purchase_date"
    cursor.execute(query2, (username))
    data2 = cursor.fetchone()

    # monthly # of tickets sold (latest year)
    query4 = "Select month(purchase_date) as month, count(ticket_id)\
            From ticket join purchases using (ticket_id) join airline_staff using (airline_name)\
            Where airline_staff.username = %s and year(purchase_date)=year(curdate())\
            group by month"
    cursor.execute(query4, (username))
    data4 = cursor.fetchall()

    # direct revenue and indirect revenue in last month
    query5 = "Select sum(case when booking_agent_id is null then price else 0 end) as direct_revenue, sum(case when booking_agent_id is null then 0 else price end) as indirect_revenue\
            From purchases join ticket using(ticket_id) join flight using(flight_num, airline_name) join airline_staff using(airline_name)\
            Where username=%s and date_sub(curdate(), interval 1 month)<=purchase_date;"
    cursor.execute(query5, (username))
    data5 = cursor.fetchall()

    # direct revenue and indirect revenue in last year
    query6 = "Select sum(case when booking_agent_id is null then price else 0 end) as direct_revenue, sum(case when booking_agent_id is null then 0 else price end) as indirect_revenue\
            From purchases join ticket using(ticket_id) join flight using(flight_num, airline_name) join airline_staff using(airline_name)\
            Where username=%s and date_sub(curdate(), interval 1 year)<=purchase_date;"
    cursor.execute(query6, (username))
    data6 = cursor.fetchall()
    cursor.close()

    context={'data1':data1, 'data2':data2, 'data3':[''], 'data4':data4, 'data5':data5, 'data6':data6}

    return render_template('staff_reports.html', username=username, **context)

@app.route('/staff/report_time', methods=['GET', 'POST'])
def staff_report_time():
    username = session['username']
    cursor = conn.cursor()
    query1 = "Select count(distinct ticket_id)\
            From ticket join purchases using (ticket_id) join airline_staff using (airline_name)\
            Where airline_staff.username = %s and date_sub(curdate(), interval 1 year)<=purchase_date"
    cursor.execute(query1, (username))
    data1 = cursor.fetchone()

    query2 = "Select count(distinct ticket_id)\
            From ticket join purchases using (ticket_id) join airline_staff using (airline_name)\
            Where airline_staff.username = %s and date_sub(curdate(), interval 1 month)<=purchase_date"
    cursor.execute(query2, (username))
    data2 = cursor.fetchone()
    
    from_date = request.form['from_date']
    to_date = request.form['to_date']
    query3 = "Select count(distinct ticket_id)\
            From ticket join purchases using (ticket_id) join airline_staff using (airline_name)\
            Where airline_staff.username = %s and purchase_date between %s and %s"
    cursor.execute(query3, (username, from_date,to_date))
    data3 = cursor.fetchone()

    query4 = "Select month(purchase_date) as month, count(ticket_id)\
            From ticket join purchases using (ticket_id) join airline_staff using (airline_name)\
            Where airline_staff.username = %s and year(purchase_date)=year(curdate())\
            group by month"
    cursor.execute(query4, (username))
    data4 = cursor.fetchall()

    query5 = "Select sum(case when booking_agent_id is null then price else 0 end) as direct_revenue, sum(case when booking_agent_id is null then 0 else price end) as indirect_revenue\
            From purchases join ticket using(ticket_id) join flight using(flight_num, airline_name) join airline_staff using(airline_name)\
            Where username=%s and date_sub(curdate(), interval 1 month)<=purchase_date;"
    cursor.execute(query5, (username))
    data5 = cursor.fetchall()

    query6 = "Select sum(case when booking_agent_id is null then price else 0 end) as direct_revenue, sum(case when booking_agent_id is null then 0 else price end) as indirect_revenue\
            From purchases join ticket using(ticket_id) join flight using(flight_num, airline_name) join airline_staff using(airline_name)\
            Where username=%s and date_sub(curdate(), interval 1 year)<=purchase_date;"
    cursor.execute(query6, (username))
    data6 = cursor.fetchall()
    cursor.close()

    context={'data1':data1, 'data2':data2, 'data3':data3, 'data4':data4, 'data5':data5, 'data6':data6}
    return render_template('staff_reports.html', username=username, **context)

app.secret_key = 'some key that you will never guess'

if __name__ == '__main__':
    app.run('127.0.0.1', 5000, debug=True)