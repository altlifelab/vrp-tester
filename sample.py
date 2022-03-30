import VRP_Gen_5 as gen
from jinja2 import Environment,Template,FileSystemLoader
in_data = {"trip_info":
               {"num_vehicles":6,
                "trip_time":"17/03/2022 16:00:00",
                "max_dist":6300,"bike_capacity":15,
                "measure_type":"duration"},
           "vehicle_info":[
               {"vehicle_id":"B1","capacity":15},
               {"vehicle_id":"B2","capacity":15},
               {"vehicle_id":"B3","capacity":15},
               {"vehicle_id":"B4","capacity":15},
               {"vehicle_id":"B5","capacity":15},
               {"vehicle_id":"B6","capacity":15}
           ],
           "location_info":[{"customer_id":1,"customer_name*":"Altlifelab Kitchen","latitude":12.924731,"longitude":77.618645,"wait_time":"00:00:00"},{"customer_id":"92","customer_name*":"Vivek Subramanyam - Office-Advance-NM-Veg","latitude":12.93028,"longitude":77.63092,"wait_time":"00:01:30"},{"customer_id":"1101","customer_name*":"Vivek Khare - Home-Advance-Egg","latitude":12.9256328,"longitude":77.677937,"wait_time":"00:00:00"},{"customer_id":"1017","customer_name*":"Vashistha Iyer - Office-Advance-Non Veg","latitude":12.9121658,"longitude":77.6506866,"wait_time":"00:01:30"},{"customer_id":"1024","customer_name*":"Suneeth Katarki - Home-Advance-Egg","latitude":13.0104305,"longitude":77.5577364,"wait_time":"00:01:30"},{"customer_id":"1106","customer_name*":"Srirama Murthy - Home-Advance-Veg","latitude":12.9641411,"longitude":77.7168758,"wait_time":"00:01:30"},{"customer_id":"1043","customer_name*":"Sireesha Boyanapalli - Home-Advance-NM-Veg","latitude":12.9060576,"longitude":77.7034716,"wait_time":"00:01:30"},{"customer_id":"1178","customer_name*":"Shylaja Balakrishnan - Home-Advance-Egg","latitude":13.0376633,"longitude":77.5458015,"wait_time":"00:01:30"},{"customer_id":"1157","customer_name*":"Shivani Saxena - Home-Advance-Non Veg","latitude":12.8994244,"longitude":77.620856,"wait_time":"00:01:30"},{"customer_id":"931","customer_name*":"Shilpi Mishra - Home-Advance-Veg","latitude":12.9285216,"longitude":77.6953331,"wait_time":"00:01:30"},{"customer_id":"976","customer_name*":"Sharad Talwar - Home-Advance-Non Veg","latitude":12.9196245,"longitude":77.6888967,"wait_time":"00:01:30"},{"customer_id":"1142","customer_name*":"Saroj Kachhwal Verma - Home-Advance-NM-Veg","latitude":12.8944716,"longitude":77.6634173,"wait_time":"00:01:30"},{"customer_id":"1137","customer_name*":"Saksham Agrawal - Home-Advance-Veg","latitude":12.9295556,"longitude":77.6874416,"wait_time":"00:01:30"},{"customer_id":"1125","customer_name*":"Sachin Shewale - Home-Advance-Egg","latitude":12.9674553,"longitude":77.7101854,"wait_time":"00:01:30"},{"customer_id":"1176","customer_name*":"Revathi Viswanathan - Home-Advance-Veg","latitude":12.9797967,"longitude":77.6922843,"wait_time":"00:01:30"},{"customer_id":"1035","customer_name*":"Renu Kashyap - Home-Advance-NM-Veg","latitude":13.1175296,"longitude":77.5773013,"wait_time":"00:01:30"},{"customer_id":"953","customer_name*":"Raktim Singh - Home-Advance-Non Veg","latitude":12.9048863,"longitude":77.6003559,"wait_time":"00:01:30"},{"customer_id":"272","customer_name*":"Rajinder Singh - Home-Advance-Non Veg","latitude":12.9193455,"longitude":77.6292008,"wait_time":"00:01:30"},{"customer_id":"1150","customer_name*":"Rajeshwari P - Home-Advance-Veg","latitude":12.9881289,"longitude":77.6845032,"wait_time":"00:01:30"},{"customer_id":"940","customer_name*":"Rajesh Nair - Home-Advance-Non Veg","latitude":12.879458,"longitude":77.760093,"wait_time":"00:01:30"},{"customer_id":"1146","customer_name*":"Rahul Hirve - Home-Advance-Non Veg","latitude":13.035273,"longitude":77.5924817,"wait_time":"00:01:30"},{"customer_id":"1058","customer_name*":"Nea Nicel - Home-Advance-Non Veg","latitude":12.9704057,"longitude":77.6749602,"wait_time":"00:00:00"},{"customer_id":"1082","customer_name*":"Naveen BM - Home-Advance-NM-Veg","latitude":12.9026002,"longitude":77.5647134,"wait_time":"00:01:30"},{"customer_id":"1153","customer_name*":"Narasimha Prasad N - Home-Advance-NM-Veg","latitude":12.9226044,"longitude":77.5516449,"wait_time":"00:01:30"},{"customer_id":"663","customer_name*":"Mridul Arora - Home-Advance-Non Veg","latitude":12.922063,"longitude":77.6917799,"wait_time":"00:01:30"},{"customer_id":"994","customer_name*":"Mahadevan Govindarajan - Home-Advance-Non Veg","latitude":12.8651613,"longitude":77.7696325,"wait_time":"00:01:30"},{"customer_id":"196","customer_name*":"Kartik Sarwade - Home-Advance-Non Veg","latitude":12.8884984,"longitude":77.5911424,"wait_time":"00:01:30"},{"customer_id":"1127","customer_name*":"Jerald Joseph - Home-Advance-Non Veg","latitude":12.9261293,"longitude":77.6655585,"wait_time":"00:01:30"},{"customer_id":"435","customer_name*":"Devika Vyas - Home-Advance-Egg","latitude":12.9193455,"longitude":77.6292008,"wait_time":"00:01:30"},{"customer_id":"394","customer_name*":"Deepa Jayaraman - Home-Advance-Egg","latitude":12.9576858,"longitude":77.7412671,"wait_time":"00:01:30"},{"customer_id":"102","customer_name*":"Bhanu - Home-Advance-Egg","latitude":12.93887,"longitude":77.54484,"wait_time":"00:01:30"},{"customer_id":"396","customer_name*":"Balaji Venkatesh S - New Home Address-Advance-Veg","latitude":12.957619,"longitude":77.7412928,"wait_time":"00:01:30"},{"customer_id":" ","customer_name*":"Balaji G - Home-Ecom","latitude":12.915212,"longitude":77.589124,"wait_time":"00:01:30"},{"customer_id":"655","customer_name*":"Asvini kumar - Home-Advance-Veg","latitude":12.9966707,"longitude":77.6594519,"wait_time":"00:01:30"},{"customer_id":"191","customer_name*":"Arvind Pani - Home-Advance-Veg","latitude":12.8426543,"longitude":77.7250889,"wait_time":"00:01:30"},{"customer_id":"1067","customer_name*":"Anshu Verma - Home-Advance-NM-Veg","latitude":12.8944716,"longitude":77.6634173,"wait_time":"00:01:30"},{"customer_id":"1155","customer_name*":"Amrit Pal Singh - Home-Advance-NM-Veg","latitude":12.8994244,"longitude":77.620856,"wait_time":"00:01:30"},{"customer_id":"1092","customer_name*":"Adithi Kesarla - Home-Advance-Veg","latitude":12.8802588,"longitude":77.587021,"wait_time":"00:01:30"},{"customer_id":" ","customer_name*":"Abhay Kulkarni - Home-Ecom","latitude":12.9169573,"longitude":77.5778016,"wait_time":"00:01:30"}]}

run = gen.vrp_generator(in_data)

print("================================================================================")
base_route="""https://www.google.com/maps/dir/?api=1&origin={depot}&destination={depot}&waypoints={waypoints}"""
waypoint="{lat}%2C{long}%7C"
routes=[]
for route in run.get("solution_detail"):
    rep_line = """Route :{vehicle_id} : No of stops : {stops}, Cumulative Time:{cum_time} " \
Last Drop:{last_drop}\nCust List =>{cust_list}\n
Route Link: {route_link}\n
==========================================================================================="""
    vehicle_id=route.get("vehicle_id")
    stops=len(route.get("route")) -1
    cust_list=[item.get("customer_name*").split("-")[0] for item in route.get("route")]
    cum_time=route.get("route")[-1].get("cum_time")
    last_drop=route.get("route")[-2].get("cum_time")
    depot=str(route.get("route")[0].get("latitude"))+"%2C"+str(route.get("route")[0].get("longitude"))
    waypoints=""
    route_stops=[]
    for stop in route.get("route"):
        if stop.get("customer_name*") !="Altlifelab Kitchen":
            waypoints+=waypoint.format(lat=stop.get("latitude"),long=stop.get("longitude"))
            stop_info={'client':stop.get("customer_name*"),'location':str(stop.get("latitude"))+","+str(stop.get("longitude"))}
            route_stops.append(stop_info)
    route_link=base_route.format(depot=depot, waypoints=waypoints)
    routes.append(route_stops)
    print(rep_line.format(vehicle_id=vehicle_id,stops=stops,cum_time=cum_time, last_drop=last_drop,cust_list=cust_list, route_link=route_link))
tfile = "routing_template.html"
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template(tfile)
output = template.render(route_info=routes)
with open("Routing Plan.html","w") as fh:
    fh.write(output)
    fh.close()



