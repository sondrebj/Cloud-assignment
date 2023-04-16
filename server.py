#to run this server, run the following command in the terminal
# python backend/server.py - http://127.0.0.1:5000/ 
import os
import vobject # use this to read vcard file
from flask import Flask, request, jsonify, send_file, Response, render_template
from database import get_database
from bson import ObjectId
app = Flask(__name__, template_folder='../public')



@app.route('/')
def index():
    return 'Welcome to the VCard App! To access the .html pages type in /upload.html or /contacts. Go to /upload.html to upload a .vcf file. And /contacts to see all the data in the database.'

# route that handles the upload functioanlity. changes the content to .json from .vcf format and sends it to the database
@app.route('/upload.html', methods=['GET', 'POST'])
def upload_vcard():
    if request.method == 'POST':
        vcard_file = request.files['file']
        vcard_content = vcard_file.read().decode('utf-8')
        vcards = vobject.readComponents(vcard_content)

        inserted_ids = []
        # for loop that goes through each instance of vcard in the uploaded .vcf file and sends the data to the database
        for vcard in vcards:
            # below is the data that will be extracted from the .vcf file the user uploads
            # and if the .vcf file they submit doesnt have a value or is missing some fields
            # then the code will assign them an emtpty value so the .vcf file can be uploaded to the database
            company = ""
            try:
                company = str(vcard.org.value[0])
            except AttributeError:
                pass

            address = ""
            try:
                address = str(vcard.adr.value)
            except AttributeError:
                pass

            phone = ""
            try:
                phone = str(vcard.tel.value)
            except AttributeError:
                pass

            bday = ""
            try:
                bday = vcard.bday.value
            except AttributeError:
                pass

            name = ""
            try:
                name = str(vcard.n.value)
            except AttributeError:
                pass

            fullname = ""
            try:
                fullname = vcard.fn.value
            except AttributeError:
                pass

            email = ""
            try:
                email = vcard.email.value
            except AttributeError:
                pass

            data = {
                'bday': bday,
                'name': name,
                'fullname': fullname,
                'company': company,
                'address': address,
                'phone': phone,
                'email': email
            }

            collection = get_database()
            result = collection.insert_one(data)
            inserted_ids.append(str(result.inserted_id))

        # when successfully inserting data, the ids will be presented along with a success message
        return jsonify({'message': 'Data inserted successfully', 'ids': inserted_ids}) 
    else:
        return send_file('../public/upload.html')

# added a general route that gets all the data from the database and displays it. Return as .json
@app.route('/contacts', methods=['GET'])
def get_all_contacts_json():
    collection = get_database()
    result = collection.find()
    data = []
    for doc in result:
        doc['_id'] = str(doc['_id'])
        data.append(doc)
    return jsonify(data)

# added a route so we can get data based on a specific id. Return as .json
@app.route('/contacts/<string:id>', methods=['GET'])
def get_by_id_json(id):
    collection = get_database()
    result = collection.find_one({"_id": ObjectId(id)})
    if result is None: # if no data based on id then display this msg
        return jsonify({'error': 'Data not found'}), 404
    result['_id'] = str(result['_id'])
   # return jsonify(result)
    return render_template('test.html', result=result)



# VCARD REQUESTS BELOW

# the same route as /contacts/ but this will return it as a .vcf format instead of json
@app.route('/contacts/vcard', methods=['GET'])
def get_all_contacts_vcard():
    collection = get_database()
    result = collection.find()
    if result is None: 
        return jsonify({'error': 'Data not found'}), 404
    
    vcards = []

    #for loop that goes through instance in the database and shows it on screen
    for r in result:
        # convert the data to .vcf format
        vcard_content = "BEGIN:VCARD\nVERSION:4.0\n"

        vcard_content += "BDAY:{}\n".format(r['bday'])
        vcard_content += "N:{}\n".format(r['name'])
        vcard_content += "FN:{}\n".format(r['fullname'])
        vcard_content += "ORG:{}\n".format(r['company'])
        vcard_content += "ADR;TYPE=WORK:;;{};;;;\n".format(r['address'])
        vcard_content += "TEL;TYPE=WORK,VOICE:{}\n".format(r['phone'])
        vcard_content += "EMAIL;TYPE=INTERNET:{}\n".format(r['email'])

        vcard_content += "X-MONGODB-ID:{}\n".format(str(r['_id'])) # include the mongoDB id 
        vcard_content += "END:VCARD\n"
        vcards.append(vcard_content)


    #uses contacts_vcard.html to render all the data as in .vcf format
    return render_template('contacts_vcard.html', vcards=vcards)


# this is the same code as above but inside a JSON structure.
# the reason for this is because i wasnt sure what you meant with this (But inside a JSON structure). 
# so i provided it as .vcf format inside a .json structure(?) and as a normal .vcf format as above
@app.route('/contacts/vcard/json', methods=['GET'])
def get_all_contacts_vcard_json():
    collection = get_database()
    result = collection.find()
    if result is None: 
        return jsonify({'error': 'Data not found'}), 404
    
    vcards = []

    for r in result:
        vcard_content = "BEGIN:VCARD\nVERSION:4.0\n"

        vcard_content += "BDAY:{}\n".format(r['bday'])
        vcard_content += "N:{}\n".format(r['name'])
        vcard_content += "FN:{}\n".format(r['fullname'])
        vcard_content += "ORG:{}\n".format(r['company'])
        vcard_content += "ADR;TYPE=WORK:;;{};;;;\n".format(r['address'])
        vcard_content += "TEL;TYPE=WORK,VOICE:{}\n".format(r['phone'])
        vcard_content += "EMAIL;TYPE=INTERNET:{}\n".format(r['email'])

        vcard_content += "X-MONGODB-ID:{}\n".format(str(r['_id'])) # include the mongoDB id 
        vcard_content += "END:VCARD\n"
        vcards.append(vcard_content)

    # Return the vcards as a JSON structure
    return jsonify({'vcards': vcards})



# this searches for a specific id and then return all the data assosiated with that id in .vcf format
@app.route('/contacts/<string:id>/vcard', methods=['GET'])
def get_by_id_vcard(id):
    collection = get_database()
    result = collection.find_one({"_id": ObjectId(id)})
    if result is None: 
        return jsonify({'error': 'Data not found'}), 404
    result['_id'] = str(result['_id'])
    
    vcard_content = "BEGIN:VCARD\nVERSION:4.0\n"
    
    vcard_content += "BDAY:{}\n".format(result['bday']) 
    vcard_content += "N:{}\n".format(result['name'])
    vcard_content += "FN:{}\n".format(result['fullname'])
    vcard_content += "ORG:{}\n".format(result['company'])
    vcard_content += "ADR;TYPE=WORK:;;{};;;;\n".format(result['address'])
    vcard_content += "TEL;TYPE=WORK,VOICE:{}\n".format(result['phone'])
    vcard_content += "EMAIL;TYPE=INTERNET:{}\n".format(result['email'])

    vcard_content += "X-MONGODB-ID:{}\n".format(str(result['_id'])) 
    vcard_content += "END:VCARD\n"
    return render_template('vcard.html', vcard=vcard_content)


# i did the same here as with this route('/contacts/vcard/json')
# because again im unsure what you mean by (But inside a JSON structure)
# so provided in both .vcf format and .vcf format inside a .json structure
@app.route('/contacts/<string:id>/vcard/json', methods=['GET'])
def get_by_id_vcard_json(id):
    collection = get_database()
    result = collection.find_one({"_id": ObjectId(id)})
    if result is None: 
        return jsonify({'error': 'Data not found'}), 404
    result['_id'] = str(result['_id'])
    
    vcard_content = "BEGIN:VCARD\nVERSION:4.0\n"
    
    vcard_content += "BDAY:{}\n".format(result['bday']) 
    vcard_content += "N:{}\n".format(result['name'])
    vcard_content += "FN:{}\n".format(result['fullname'])
    vcard_content += "ORG:{}\n".format(result['company'])
    vcard_content += "ADR;TYPE=WORK:;;{};;;;\n".format(result['address'])
    vcard_content += "TEL;TYPE=WORK,VOICE:{}\n".format(result['phone'])
    vcard_content += "EMAIL;TYPE=INTERNET:{}\n".format(result['email'])

    vcard_content += "X-MONGODB-ID:{}\n".format(str(result['_id'])) 
    vcard_content += "END:VCARD\n"
    
    vcard_lines = vcard_content.split('\n')
    vcard_dict = {'vcard': '\n'.join(vcard_lines)}
    
    return jsonify(vcard_dict)



# route for downloading all the data in the database as a .vcf file    
@app.route('/contacts/vcard/download', methods=['GET'])
def get_all_vcards():
    collection = get_database()
    all_vcards = collection.find()
    
    vcard_content = ""
    
    for result in all_vcards:
        result['_id'] = str(result['_id'])
        
        vcard_content += "BEGIN:VCARD\nVERSION:4.0\n"
        vcard_content += "BDAY:{}\n".format(result['bday']) 
        vcard_content += "N:{}\n".format(result['name'])
        vcard_content += "FN:{}\n".format(result['fullname'])
        vcard_content += "ORG:{}\n".format(result['company'])
        vcard_content += "ADR;TYPE=WORK:;;{};;;;\n".format(result['address'])
        vcard_content += "TEL;TYPE=WORK,VOICE:{}\n".format(result['phone'])
        vcard_content += "EMAIL;TYPE=INTERNET:{}\n".format(result['email'])
        vcard_content += "END:VCARD\n"
        vcard_content += "\n"  # add a newline after each vcard
    
    response = Response(vcard_content, mimetype='text/x-vcard')
    response.headers.set('Content-Disposition', 'attachment', filename='all_contacts.vcf')
    
    return response


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv('PORT', default=5000))


#if __name__ == "__main__":
 #   app.run(debug=True)

