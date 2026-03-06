import os
from flask import Flask, render_template, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Raspberry Pi systemd environment ke liye absolute path fix
# Taki instance folder ka koi chakkar na rahe
DB_PATH = '/home/pi/cubix_app/cubix_inventory.db'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- DATABASE MODELS ---

class Filament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    type = db.Column(db.String(50))
    color_hex = db.Column(db.String(10))
    full_spools = db.Column(db.Integer, default=0)
    half_spools = db.Column(db.Integer, default=0)
    purchase_date = db.Column(db.String(20))

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "type": self.type, 
            "colorHex": self.color_hex, "fullSpools": self.full_spools, 
            "halfSpools": self.half_spools, "purchaseDate": self.purchase_date
        }

class Printer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    slot0 = db.Column(db.Integer, nullable=True)
    slot1 = db.Column(db.Integer, nullable=True)
    slot2 = db.Column(db.Integer, nullable=True)
    slot3 = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, 
            "slots": [self.slot0, self.slot1, self.slot2, self.slot3]
        }

class UsageLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    log_type = db.Column(db.String(20)) # 'RESTOCK' or 'ARCHIVE'
    filament_name = db.Column(db.String(100))
    type = db.Column(db.String(50))
    color_hex = db.Column(db.String(10))
    printer_name = db.Column(db.String(100), nullable=True)
    slot_num = db.Column(db.Integer, nullable=True)
    qty = db.Column(db.Integer, default=0)
    purchase_date = db.Column(db.String(20), nullable=True)
    date = db.Column(db.String(50))
    log_time = db.Column(db.String(20))
    filter_date = db.Column(db.String(20))
    notes = db.Column(db.String(200), nullable=True)

    def to_dict(self):
        return {
            "id": self.id, "logType": self.log_type, "filamentName": self.filament_name,
            "type": self.type, "colorHex": self.color_hex, "printerName": self.printer_name,
            "slotNum": self.slot_num, "qty": self.qty, "purchaseDate": self.purchase_date,
            "date": self.date, "logTime": self.log_time, "filterDate": self.filter_date,
            "notes": self.notes
        }

# --- ROUTES & API ENDPOINTS ---

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    filaments = [f.to_dict() for f in Filament.query.all()]
    printers = [p.to_dict() for p in Printer.query.all()]
    logs = [l.to_dict() for l in UsageLog.query.order_by(UsageLog.id.desc()).all()]
    return jsonify({"filaments": filaments, "printers": printers, "logs": logs})

@app.route('/api/backup', methods=['GET'])
def backup_db():
    if os.path.exists(DB_PATH):
        # Live database download karein
        return send_file(DB_PATH, as_attachment=True, download_name=f"cubix_backup_{datetime.now().strftime('%Y%m%d')}.db")
    return "Database file not found on Pi.", 404

@app.route('/api/filament/add', methods=['POST'])
def add_filament():
    data = request.json
    new_fil = Filament(
        name=data['name'], type=data['type'], color_hex=data['colorHex'],
        full_spools=data['fullSpools'], half_spools=data['halfSpools'],
        purchase_date=data['purchaseDate']
    )
    db.session.add(new_fil)
    db.session.commit()
    
    if data['fullSpools'] > 0:
        now = datetime.now()
        log = UsageLog(
            log_type='RESTOCK', filament_name=new_fil.name, type=new_fil.type,
            color_hex=new_fil.color_hex, qty=new_fil.full_spools, 
            date=data['purchaseDate'], filter_date=data['purchaseDate'],
            log_time=now.strftime("%I:%M %p")
        )
        db.session.add(log)
        db.session.commit()
    return jsonify({'success': True})

@app.route('/api/filament/edit', methods=['POST'])
def edit_filament():
    data = request.json
    fil = Filament.query.get(data['id'])
    if fil:
        fil.name = data['name']
        fil.type = data['type']
        fil.color_hex = data['colorHex']
        db.session.commit()
    return jsonify({'success': True})

@app.route('/api/filament/restock', methods=['POST'])
def restock_filament():
    data = request.json
    fil = Filament.query.get(data['id'])
    if fil:
        fil.full_spools += data['qty']
        fil.purchase_date = data['dateStr']
        now = datetime.now()
        log = UsageLog(
            log_type='RESTOCK', filament_name=fil.name, type=fil.type,
            color_hex=fil.color_hex, qty=data['qty'], 
            date=data['dateStr'], filter_date=data['dateStr'],
            log_time=now.strftime("%I:%M %p")
        )
        db.session.add(log)
        db.session.commit()
    return jsonify({'success': True})

@app.route('/api/stock/update', methods=['POST'])
def update_stock():
    data = request.json
    fil = Filament.query.get(data['id'])
    if fil:
        if data['countType'] == 'full':
            fil.full_spools += 1 if data['action'] == 'plus' else -1
            if fil.full_spools < 0: fil.full_spools = 0
        else:
            fil.half_spools += 1 if data['action'] == 'plus' else -1
            if fil.half_spools < 0: fil.half_spools = 0
        db.session.commit()
    return jsonify({'success': True})

@app.route('/api/printer/add', methods=['POST'])
def add_printer():
    data = request.json
    new_printer = Printer(name=data['name'])
    db.session.add(new_printer)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/ams/load', methods=['POST'])
def load_ams():
    data = request.json
    printer = Printer.query.get(data['printerId'])
    fil = Filament.query.get(data['filamentId'])
    if printer and fil:
        if data['loadType'] == 'new' and fil.full_spools > 0:
            fil.full_spools -= 1
        elif data['loadType'] == 'existing' and fil.half_spools > 0:
            fil.half_spools -= 1
        setattr(printer, f"slot{data['slotIdx']}", fil.id)
        db.session.commit()
    return jsonify({'success': True})

@app.route('/api/ams/unload', methods=['POST'])
def unload_ams():
    data = request.json
    printer = Printer.query.get(data['printerId'])
    if printer:
        fil_id = getattr(printer, f"slot{data['slotIdx']}")
        if fil_id:
            fil = Filament.query.get(fil_id)
            if fil: fil.half_spools += 1
            setattr(printer, f"slot{data['slotIdx']}", None)
            db.session.commit()
    return jsonify({'success': True})

@app.route('/api/ams/archive', methods=['POST'])
def archive_ams():
    data = request.json
    printer = Printer.query.get(data['printerId'])
    if printer:
        fil_id = getattr(printer, f"slot{data['slotIdx']}")
        if fil_id:
            fil = Filament.query.get(fil_id)
            if fil:
                now = datetime.now()
                log = UsageLog(
                    log_type='ARCHIVE', filament_name=fil.name, type=fil.type,
                    color_hex=fil.color_hex, printer_name=printer.name,
                    slot_num=data['slotIdx'], purchase_date=fil.purchase_date,
                    date=now.strftime("%m/%d/%Y"), log_time=now.strftime("%I:%M %p"),
                    filter_date=now.strftime("%Y-%m-%d"), notes=data.get('notes', '')
                )
                db.session.add(log)
            setattr(printer, f"slot{data['slotIdx']}", None)
            db.session.commit()
    return jsonify({'success': True})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
