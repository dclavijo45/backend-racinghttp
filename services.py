from pkcs7 import *
from Crypto import Random
from Crypto.Cipher import AES
from Crypto import Random 
from config import KEY_TOKEN_AUTH
from config import SECRET_KEY, MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_DB
from config import MYSQL_PASSWORD
import random
import jwt
import base64
import time
import mysql.connector
import datetime
import bcrypt

def fixStringClient(string):
    fixed = str(string).replace("'", "").replace("*", "").replace('"', "").replace("+", "").replace("|", "").replace("%", "").replace("$", "").replace("&", "").replace("=", "").replace("?", "").replace('¡', "").replace("\a", "").replace("<", "").replace(">", "").replace("/", "").replace("[", "").replace("]", "").replace("(", "").replace("]", "").replace("´", "").replace(",", "").replace("!", "").replace("\n", "")
    return fixed

def checkJwt(token):
    try:
        data = jwt.decode(token, KEY_TOKEN_AUTH , algorithms=['HS256'])
        return True
    except:
        return False

def dataTableMysql(query, rtn="datatable"):
    try:
        mydb = mysql.connector.connect(host=MYSQL_HOST,user=MYSQL_USER,password=MYSQL_PASSWORD,database=MYSQL_DB)
        #print("OP 1")
        mycursor = mydb.cursor()
        #print("OP 2")
        #print(query)
        mycursor.execute(query)
        #print("OP 3")
        data = mycursor.fetchall()
        #print("OP 4")
        mydb.commit()
        #print("OP 5")
        
        if rtn == "datatable":
            mycursor.close()
            return data
        elif rtn == "rowcount":
            #print(mycursor.rowcount)
            if mycursor.rowcount >= 1:
                mycursor.close()
                return True
            else:
                mycursor.close()
                return False
        else:
            mycursor.close()
            return data
    except:
        return False

def encoded_jwt(user_id):
    return jwt.encode({'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=180), 'user_id': user_id}, KEY_TOKEN_AUTH , algorithm='HS256')

def cryptStringBcrypt(string, rtn="string"):
    s = random.randint(5,10)
    salt = bcrypt.gensalt(s)
    hashed = bcrypt.hashpw(bytes(str(string), encoding= 'utf-8'), salt)
    if rtn == "string":
        return hashed.decode("utf-8")
    elif rtn == "byte":
        return hashed
    else:
        return hashed.decode("utf-8")

def decryptStringBcrypt(EncValidate, EncCompare):
    return bcrypt.checkpw(bytes(str(EncValidate), encoding= 'utf-8'), EncCompare)

def getBigRandomString():
    return str(random.randint(random.randint(round(time.time() + 2), round(time.time()) + round(time.time() + 8)), round(time.time() - 3)*round(time.time())+1))

def getMinRandomString():
    try:
        rand1 = random.randint(int(str(round(time.time()))[::-5][::2]),int(str(round(time.time()))[::-5][::2]))
        rand2 = random.randint(int(str(round(time.time()))[::-5][::2]),int(str(round(time.time()))[::-5][::2]))
        return str(random.randint(rand1, rand2+10))
    except :
        return str(random.randint(6, 15))

def cryptBase64(string):
    try:
        m_byte = string.encode('ascii')
        b64_b = base64.b64encode(m_byte)
        return b64_b.decode('ascii')
    except :
        return False

def decryptBase64(b_64):
    try:
        b64_b = b_64.encode('ascii')
        m_b = base64.b64decode(b64_b)
        return m_b.decode('ascii')
    except :
        return False

def CryptData(text, custom="none"):
    """
    master_key: random string based on string {crypt}

    CryptData( String = string to encrypt , String = custom_master_key -- or empty to default )

    return Array[] = [ encrypted string, master_key ]
    """
    try:
        crypt = ''
        if custom != "none" and custom != "random":
            crypt = custom
        elif custom == "random":
            sizeC = len('abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMOPQRSTUVWXYZ+/= :}{')
            crypt = random.sample('abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMOPQRSTUVWXYZ+/= :}{', sizeC)
            cryptJoin = ''.join(crypt)
            bcryptR = random.sample(cryptJoin, len(cryptJoin))
            #print(len(bcrypt))
            b_end = ''.join(bcryptR)

            r_crypt = str.maketrans (cryptJoin, b_end)
            return [text.translate(r_crypt), b_end, cryptJoin]
            print("Random")
        else:
            crypt = 'abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMOPQRSTUVWXYZ+/= :}{'
        size = len(crypt)
        bcryptR = random.sample(crypt, size)
        #print(len(bcrypt))
        b_end = ''.join(bcryptR)

        r_crypt = str.maketrans (crypt, b_end)
        return [text.translate(r_crypt), b_end]
    except:
        return [False, False]

def encWithPass(clear_text,  master_key):
    try:
        encoder = PKCS7Encoder()
        raw = encoder.encode(clear_text)
        iv = Random.new().read(16)
        cipher = AES.new( master_key, AES.MODE_CBC, iv, segment_size=128 )
        return base64.b64encode( iv + cipher.encrypt( raw ) ).decode("utf-8")
    except :
        return False
    
def decode_jwt(jwtx):
    try:
        return jwt.decode(jwtx, KEY_TOKEN_AUTH , algorithms=['HS256'])
    except :
        return False

def initChat(id_provisional_receptor, id_provisional_emisor):
    try:
        get_pv_info = dataTableMysql("SELECT id_provisional, llave_privada FROM usuarios WHERE id_provisional = %s", (id_provisional_receptor,))
        if len(get_pv_info) >= 1:
            private_key = ''
            for data in get_pv_info:
                private_key = data[1]
            master_key = ''.join(random.sample('abcdefghijklmnopqrs)tuvwxyz0123456789ABCDEFGHIJKLMOPQRSTUVWXYZ+/= #$&=)(*-_', 32))
            access_receptor = encWithPass('{"id_emisor": %s, "master_key": %s, "id_receptor": %s}', (id_provisional_emisor, master_key, id_provisional_receptor,), private_key)
            return {"access_receptor": access_receptor,"master_key": master_key, "auth_token": True}
    except :
        return False
    
def createStringRandom(size = 0):
    try:
        if size == 0 or size > 64:
            return False
        else:
            key = 'abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMOPQRSTUVWXYZ+/='
            return ''.join(random.sample(key, size))
    except :
        return False
    