# Ueberschussladen V1.1
#
# Import some modules
import json, requests, time, datetime, threading
from decimal import Decimal
from flask import Flask, render_template, request
#from waitress import serve

# Variable declaration
state_string = 'empty state_string'
load_pwr_avg = 0
grid_pwr_avg = 0
battery_pwr_avg = 0
pv_pwr_avg = 0
charge_current_form = 6
charge_current_min = 6
charge_current_max = 16
charge_current = charge_current_min
charge_pwr_min = -1380
charge_pwr_step = -230
charge_pwr_keep = 100
charge_active = False
battery_soc = 0
battery_power_min = 4000
battery_soc_min = 60
battery_soc_full_load = 80
secsavg = 15
charge_mode = 0
charge_mode1 = "STOP - NO CHARGE"
# 0 = Stop, 1 = Auto, 2 = Fixed
wb_phase = 1
phases = 1
phases_form = 1

url_pv     = 'http://192.168.29.211/solar_api/v1/GetPowerFlowRealtimeData.fcgi'
url_wb_car = 'http://192.168.29.210/api/status?filter=car' #get car state
url_wb_amp = 'http://192.168.29.210/mqtt?payload=amx=' #Ampere (e.g. 16)
url_wb_alw = 'http://192.168.29.210/mqtt?payload=alw=' #OnOff (0 or 1)
url_wb_phase = 'http://192.168.29.210/mqtt?payload=fsp=' # Switch between 1 and 3 Phase

def get_pv_data():
	global state_string
	error = True
	while (error):
		try:
			pv_intern = json.loads(requests.get(url_pv).text)
#			time.sleep(5)
		except:
			now = datetime.datetime.now()
			state_string = now.strftime("%m/%d/%Y, %H:%M:%S") + " PV IP Error"
			print(state_string)
			time.sleep(15)
		else:
			error = False
	return pv_intern

def get_car_state():
	global state_string
	error = True
	while (error):
		try:
			car_intern = json.loads(requests.get(url_wb_car).text)
#			time.sleep(5)
		except:
			now = datetime.datetime.now()
			state_string = now.strftime("%m/%d/%Y, %H:%M:%S") + " WB IP Error while get car state"
			print(state_string)
			time.sleep(15)
		else:
			error = False
	return int(round(Decimal(car_intern['car'])))

def switch_wb_onoff(sw):
	global state_string
	if (sw == True):
		error = True
		while (error):
			try:
				requests.post(url_wb_alw+"1")
#				time.sleep(5)
			except:
				now = datetime.datetime.now()
				state_string = now.strftime("%m/%d/%Y, %H:%M:%S") + " WB IP Error while WB switch ON"
				print(state_string)
				time.sleep(15)
			else:
				error = False
	else:
		error = True
		while (error):
			try:
				requests.post(url_wb_alw+"0")
#				time.sleep(5)
			except:
				now = datetime.datetime.now()
				state_string = now.strftime("%m/%d/%Y, %H:%M:%S") + " WB IP Error while WB switch OFF"
				print(state_string)
				time.sleep(15)
			else:
				error = False

def switch_wb_amp(wb_amp):
	global state_string
	error = True
	while (error):
		try:
			requests.post(url_wb_amp+str(wb_amp))
#			time.sleep(5)
		except:
			now = datetime.datetime.now()
			state_string = now.strftime("%m/%d/%Y, %H:%M:%S") + " WB IP Error while changing current at WB"
			print(state_string)
			time.sleep(15)
		else:
			error = False

def switch_wb_phase(wb_phase):
	global state_string
	error = True
	while (error):
		try:
			if wb_phase == 3:
				requests.post(url_wb_phase+"0")
			else:
				requests.post(url_wb_phase+"1")
		except:
			now = datetime.datetime.now()
			state_string = now.strftime("%m/%d/%Y, %H:%M:%S") + " WB IP Error while changing phases at WB"
			print(state_string)
			time.sleep(15)
		else:
			error = False

def load():
        P_Load = (data['Body']['Data']['Site']['P_Load'])
        if P_Load != None:
                return int(round(Decimal(P_Load)))
        else:
                return 0

def grid():
        P_Grid = (data['Body']['Data']['Site']['P_Grid'])
        if P_Grid != None:
                return int(round(Decimal(P_Grid)))
        else:
                return 0

def battery():
        P_Battery = (data['Body']['Data']['Site']['P_Akku'])
        if P_Battery != None:
                return int(round(Decimal(P_Battery)))
        else:
                return 0

def pv():
        P_PV = (data['Body']['Data']['Site']['P_PV'])
        if P_PV != None:
                return int(round(Decimal(P_PV)))
        else:
                return 0

def soc():
        SOC = (data['Body']['Data']['Inverters']['1']['SOC'])
        if SOC != None:
                return int(SOC)
        else:
                return 0

#def one_minute_avg():
#	i = 0
#	secsavg = 15
#	load_pwr_avg_i = 0
#	grid_pwr_avg_i = 0
#	battery_pwr_avg_i = 0
#	while (i<secsavg):
#		i += 1
#		data = get_pv_data()
#		grid_pwr_avg_i = grid()/secsavg + grid_pwr_avg_i
#		load_pwr_avg_i = load()/secsavg + load_pwr_avg_i
#		battery_pwr_avg_i = battery()/secsavg + battery_pwr_avg_i
#		time.sleep(1)
#	return int(round(grid_pwr_avg_i)), int(round(load_pwr_avg_i)), int(round(battery_pwr_avg_i))

#f = open("ueberschuss.log","a")
#now = datetime.datetime.now()
#outstring = now.strftime("%m/%d/%Y, %H:%M:%S") + " START SW\n"
#f.write(outstring)
#f.close()

#data = get_pv_data()

flask_app = Flask(__name__)

@flask_app.route("/", methods=['GET', 'POST'])
def view_ueberschuss():
	global charge_mode
	global charge_mode1
	global state_string
	global charge_current
	global charge_current_form
	global phases_form
	global phases
	
	
	if request.method == 'POST':
		if request.form.get('auto') == 'AUTO':
			charge_mode = 1
			charge_mode1 = "SURPLUS CHARGE"
		elif  request.form.get('stop') == 'STOP':
			charge_mode = 0
			charge_mode1 = "STOP - NO CHARGE"
		elif  request.form.get('fixed') == 'FIXED':
			charge_mode = 2
			charge_mode1 = "FIXED CHARGE"
			charge_current_form = int(request.form.get('current'))
			phases_form = int(request.form.get('phases1'))
			if (charge_current_form > 16): charge_current_form = 16
			if (charge_current_form < 6): charge_current_form = 6
			if (phases_form != 3): phases_form = 1
		else:
			pass # unknown
	elif request.method == 'GET':
		return render_template('index.html', phases = phases, state_string = state_string, charge_mode1 = charge_mode1, charge_active = charge_active, charge_current=charge_current)
		
	return render_template('index.html', phases = phases, state_string = state_string, charge_mode1 = charge_mode1, charge_active = charge_active, charge_current=charge_current)

def run_ueberschuss():
	global charge_active
	global charge_current
	global charge_current_form
	global state_string
	global data
	global charge_mode1
	global charge_mode
	global phases
	global phases_form
	
	while True:	
		if (charge_mode < 0) or (charge_mode > 2): charge_mode = 0	
		while (charge_mode == 0):
			charge_active = False
			charge_current = charge_current_min
			switch_wb_onoff(False)
			phases = 1
			switch_wb_phase(phases)
			switch_wb_amp(charge_current)
			now = datetime.datetime.now()
			state_string = now.strftime("%m/%d/%Y, %H:%M:%S") + " switched off"
			print(state_string)
			time.sleep(60)
			
		while (charge_mode == 2):
			if (get_car_state() < 2):
				charge_active = False
				charge_current = charge_current_min
				switch_wb_onoff(False)
				switch_wb_amp(charge_current)
				now = datetime.datetime.now()
				state_string = now.strftime("%m/%d/%Y, %H:%M:%S") + " const charge - no car"
				print(state_string)
				time.sleep(60)
			else:
				charge_active = True
				charge_current = charge_current_form
				phases = phases_form
				switch_wb_amp(charge_current)
				switch_wb_phase(phases)
				switch_wb_onoff(True)
				now = datetime.datetime.now()
				state_string = now.strftime("%m/%d/%Y, %H:%M:%S") + " const charge"
				print(state_string)
				time.sleep(60)
			
		while (charge_mode == 1):
			switch_wb_onoff(False)
			phases = 1
			switch_wb_phase(phases)
			switch_wb_amp(charge_current_min)
			now = datetime.datetime.now()
			state_string = now.strftime("%m/%d/%Y, %H:%M:%S") + " auto charge (re)start"
			print(state_string)
			time.sleep(15)

			while ((charge_active == False) & (charge_mode == 1)):
				while ((get_car_state() < 2) & (charge_mode == 1)):
					now = datetime.datetime.now()
					state_string = now.strftime("%m/%d/%Y, %H:%M:%S") + " auto charge - no car"
					print(state_string)
					time.sleep(15)
				if charge_mode != 1:
					break
				charge_current = charge_current_min
				switch_wb_onoff(False)
				switch_wb_amp(charge_current)

		#		grid_pwr_avg, load_pwr_avg, battery_pwr_avg = one_minute_avg()
				i = 0
				load_pwr_avg = 0
				grid_pwr_avg = 0
				pv_pwr_avg = 0
				battery_pwr_avg = 0
				while (i<secsavg):
					i += 1
					data = get_pv_data()
					grid_pwr_avg = grid()/secsavg + grid_pwr_avg
					grid_pwr_avg = int(grid_pwr_avg)
					load_pwr_avg = load()/secsavg + load_pwr_avg
					load_pwr_avg = int(load_pwr_avg)
					battery_pwr_avg = battery()/secsavg + battery_pwr_avg
					battery_pwr_avg = int(battery_pwr_avg)
					pv_pwr_avg = pv()/secsavg + pv_pwr_avg
					pv_pwr_avg = int(pv_pwr_avg)
					time.sleep(1)
					
				battery_soc = soc()

				surplus_power = grid_pwr_avg
				if (battery_soc >= battery_soc_min):
					if (battery_soc >= battery_soc_full_load):
						if (battery_pwr_avg > 100):
							surplus_power = grid_pwr_avg + battery_pwr_avg
						elif (battery_pwr_avg < -1000):
							surplus_power = grid_pwr_avg - 500
					else:
						if (battery_pwr_avg > 100):
							surplus_power = grid_pwr_avg + battery_pwr_avg

					if (surplus_power < charge_pwr_min):
						charge_active = True
						switch_wb_onoff(charge_active)
						switch_wb_amp(charge_current)
						now = datetime.datetime.now()
						state_string = now.strftime("%m/%d/%Y, %H:%M:%S") + " EINSCHALTEN"
						print(state_string)
		# ein Minute warten, damit Auto sauber einschalten kann
						time.sleep(30)
				now = datetime.datetime.now()
				state_string = now.strftime("%m/%d/%Y, %H:%M:%S") + " GP:" + str(grid_pwr_avg).rjust(5) + " LP:" + str(load_pwr_avg).rjust(5) + " PV:" + str(pv_pwr_avg).rjust(5) + " BP:" + str(battery_pwr_avg).rjust(5) + " UE:" + str(surplus_power).rjust(5) + " SOC:" + str(battery_soc).rjust(3) + " Act:" + str(charge_active) + " CUR:" + str(charge_current).rjust(2)
				print(state_string)

			while ((charge_active == True) & (charge_mode == 1)):
				i = 0
				load_pwr_avg = 0
				grid_pwr_avg = 0
				battery_pwr_avg = 0
				pv_pwr_avg = 0
				while (i<secsavg):
					i += 1
					data = get_pv_data()
					grid_pwr_avg = grid()/secsavg + grid_pwr_avg
					grid_pwr_avg = int(grid_pwr_avg)
					load_pwr_avg = load()/secsavg + load_pwr_avg
					load_pwr_avg = int(load_pwr_avg)
					battery_pwr_avg = battery()/secsavg + battery_pwr_avg
					battery_pwr_avg = int(battery_pwr_avg)
					pv_pwr_avg = pv()/secsavg + pv_pwr_avg
					pv_pwr_avg = int(pv_pwr_avg)
					time.sleep(1)
				battery_soc = soc()

				surplus_power = grid_pwr_avg
				if (battery_soc >= battery_soc_min):
					if (battery_soc >= battery_soc_full_load):
						if (battery_pwr_avg > 100):
							surplus_power = grid_pwr_avg + battery_pwr_avg
						elif (battery_pwr_avg < -1000):
							surplus_power = grid_pwr_avg - 500
					else:
						if (battery_pwr_avg > 100):
							surplus_power = grid_pwr_avg + battery_pwr_avg
				
				# Leistungssprung je 1 Ampere
				if (phases != 3):
					charge_pwr_step = -230
				else:
					charge_pwr_step = -690
					
				if (surplus_power < charge_pwr_step):
					charge_current += 1
					if (charge_current > charge_current_max):
						charge_current = charge_current_max
						# maximaler Strom erreicht - checken ob 3 phasig möglich ist
						# wenn 3-phasig möglich 3-phasig einschalten
						if ((phases == 1) and (surplus_power < 3*charge_pwr_step)):
							charge_current = charge_current_min
							phases = 3
							switch_wb_amp(charge_current)
							switch_wb_phase(phases)
							now = datetime.datetime.now()
							state_string = now.strftime("%m/%d/%Y, %H:%M:%S") + " 3 Phasen ein"
							print(state_string)
							time.sleep(60)
					switch_wb_amp(charge_current)
				else:
					if (surplus_power > charge_pwr_keep):
						charge_current -= 1
						if (charge_current < charge_current_min):
							# wenn in 3-phasig
							# 3-phasig zuerst ausschalten
							if (phases == 3):
								phases = 1
								charge_current = charge_current_max
								switch_wb_phase(phases)
								switch_wb_amp(charge_current)
								now = datetime.datetime.now()
								state_string = now.strftime("%m/%d/%Y, %H:%M:%S") + " 3 Phasen aus"
								print(state_string)
								time.sleep(60)
							else:
								charge_current = charge_current_min
								charge_active = False
								switch_wb_onoff(charge_active)
								switch_wb_amp(charge_current)
								now = datetime.datetime.now()
								state_string = now.strftime("%m/%d/%Y, %H:%M:%S") + " AUSSCHALTEN"
								print(state_string)
								# 20 secs warten, damit Auto sauber ausschalten kann
								time.sleep(20)
						switch_wb_amp(charge_current)

				if (get_car_state() < 2):
					charge_current = charge_current_min
					charge_active = False
					switch_wb_onoff(charge_active)
					switch_wb_amp(charge_current)
					now = datetime.datetime.now()
					state_string = now.strftime("%m/%d/%Y, %H:%M:%S") + " Car lost - ausschalten"
					print(state_string)
				else:
					now = datetime.datetime.now()
					state_string = now.strftime("%m/%d/%Y, %H:%M:%S") + " GP:" + str(grid_pwr_avg).rjust(5) + " LP:" + str(load_pwr_avg).rjust(5) + " PV:" + str(pv_pwr_avg).rjust(5) + " BP:" + str(battery_pwr_avg).rjust(5) + " UE:" + str(surplus_power).rjust(5) + " SOC:" + str(battery_soc).rjust(3) + " Act:" + str(charge_active) + " CUR:" + str(charge_current).rjust(2) + " Pha:" + str(phases).rjust(1)
					print(state_string)

#	f = open("ueberschuss.log","a")
#	now = datetime.datetime.now()
#	outstring = now.strftime("%m/%d/%Y, %H:%M:%S") + " " + str(charge_power) + " " + str(grid()) + " " + str(ueberschuss) + " " + str(soc()) + " OFF\n"
#	f.write(outstring)
#	f.close()

if __name__ == '__main__':
    # Start a background thread to control/update the LCD
    # You'll also want to devise a graceful way to shutdown your whole app
    # by providing a kill signal to your threads, for example (beyond the scope of this answer)
    thread_ueberschuss = threading.Thread(target=run_ueberschuss, name='run_ueberschuss')
    thread_ueberschuss.start()
    # Now run the flask web server in the main thread
    # debug=False to avoid Flask printing duplicate info to the console
    flask_app.run(debug=False, host='0.0.0.0')
    #serve(flask_app, host='0.0.0.0', port=5000)
