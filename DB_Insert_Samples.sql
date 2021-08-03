delete from airline;
delete from airport;
delete from airplane;
delete from flight;
delete from ticket;
delete from airline_staff;
delete from customer;
delete from booking_agent;
delete from purchases;

insert into airline values ('China Eastern');
insert into airline values ('Spring Airlines');
insert into airline values ('Lufthansa');

insert into airport values ('JFK', 'NYC');
insert into airport values ('PVG', 'Shanghai');
insert into airport values ('AUH', 'Abu Dhabi');
insert into airport values ('HKG', 'Hong Kong');
insert into airport values ('NRT', 'Tokyo');

insert into airplane values ('China Eastern','01', 140);
insert into airplane values ('China Eastern','02', 122);
insert into airplane values ('China Eastern','03', 250);
insert into airplane values ('China Eastern','04', 230);
insert into airplane values ('China Eastern','05', 189);
insert into airplane values ('Spring Airlines','01', 150);
insert into airplane values ('Spring Airlines','02', 132);
insert into airplane values ('Spring Airlines','03', 202);
insert into airplane values ('Spring Airlines','04', 200);
insert into airplane values ('Spring Airlines','05', 320);
insert into airplane values ('Lufthansa','01', 105);
insert into airplane values ('Lufthansa','02', 230);
insert into airplane values ('Lufthansa','03', 190);

insert into flight values ('China Eastern', '0111', 'PVG', '2021-04-01 09:30:00', 'HKG', '2021-04-01 11:55:00', 1220, 'upcoming', '01');
insert into flight values ('Lufthansa', '0111', 'PVG','2021-03-29 21:45:00', 'JFK', '2021-03-30 12:50:00', 12461, 'in progress', '01');
insert into flight values ('Spring Airlines', '0102', 'HKG', '2021-06-24 13:15:00', 'PVG', '2021-06-24 16:00:00', 3153, 'delayed', '02');
insert into flight values ('Spring Airlines', '0009', 'PVG', '2021-05-24 13:15:00', 'HKG', '2021-05-24 16:00:00', 3000, 'upcoming', '03');
insert into flight values ('Spring Airlines', '0555', 'NRT', '2021-05-10 22:45:00', 'PVG', '2021-05-11 06:30:00', 4030, 'upcoming', '04');
insert into flight values ('Spring Airlines', '0333', 'AUH', '2021-04-25 12:00:05', 'PVG', '2021-04-26 9:25:00', 8979, 'upcoming', '05');

insert into airline_staff values ('ml971cne', 'e902!gwr', 'Mei', 'Liu', '1984-01-03', 'China Eastern');
insert into airline_staff values ('fw380cne', 'slh3?2e1', 'Fei', 'Wang', '1982-11-03', 'China Eastern');
insert into airline_staff values ('sw6f21spr', '10f2ur?_r', 'Sam', 'Wu', '1987-05-28', 'Spring Airlines');

insert into customer values ('lzh@gmail.com', 'Li Zhang', 'lzh1386', '13', 'Century Avenue', 'Shanghai', 'China',
                            1860382749, 'E37562394', '2022-05-27', 'China', '1998-10-02');
insert into customer values ('ryn@gmail.com', 'Rachel Yang', 'ryn3472', '01', 'Washington Square', 'NYC', 'United States',
                            1347780755, '7700225VH', '2024-11-06', 'United States', '1996-04-15');

insert into booking_agent values ('ksh@gmail.com', 'kdh_f1ow2', '099');
insert into booking_agent values ('abc@qq.com', '12345', '088');

insert into ticket (airline_name, flight_num) values ('China Eastern', '0111');
insert into ticket (airline_name, flight_num) values ('Spring Airlines', '0102');
insert into ticket (airline_name, flight_num) values ('Spring Airlines', '0102');
insert into ticket (airline_name, flight_num) values ('Spring Airlines', '0009');
insert into ticket (airline_name, flight_num) values ('Spring Airlines', '0009');
insert into ticket (airline_name, flight_num) values ('Spring Airlines', '0009');
insert into ticket (airline_name, flight_num) values ('Spring Airlines', '0555');
insert into ticket (airline_name, flight_num) values ('Spring Airlines', '0555');
insert into ticket (airline_name, flight_num) values ('Spring Airlines', '0333');
insert into ticket (airline_name, flight_num) values ('Spring Airlines', '0789');
insert into ticket (airline_name, flight_num) values ('Spring Airlines', '0789');

insert into purchases values ('1', 'lzh@gmail.com', null, '2021-03-01');
insert into purchases values ('2', 'ryn@gmail.com', '099', '2021-03-20');
insert into purchases values ('3', 'ryn@gmail.com', '088', '2021-04-30');
insert into purchases values ('4', 'jh6181@nyu.com', '108', '2021-05-07');
insert into purchases values ('5', 'ryn@gmail.com', '108', '2021-02-01');
insert into purchases values ('6', 'ryn@gmail.com', '108', '2021-04-18');
insert into purchases values ('7', 'lzh@gmail.com', '108', '2021-04-30');
insert into purchases values ('8', 'ryn@gmail.com', '108', '2021-03-01');
insert into purchases values ('9', 'ryn@gmail.com', '108', '2021-03-29');
insert into purchases values ('10', 'lzh@gmail.com', '108', '2021-04-30');
insert into purchases values ('11', 'jh6181@nyu.edu', '108', '2021-05-02');