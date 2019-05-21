from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os
import json
import datetime
from flask_jwt_simple import (
    JWTManager, jwt_required, create_jwt, get_jwt_identity
)
# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

#Setting up Flask-JWT- Simple extension
app.config['JWT_SECRET_KEY'] = 'secretkey'  # Change this!
jwt = JWTManager(app)

# Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "db.sqlite"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initializing db
db = SQLAlchemy(app)

# Class for user
class User(db.Model):
    id = db.Column(db.Integer,primary_key=True,unique=True, nullable=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    username = db.Column(db.String(20),unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    bio = db.Column(db.String(150))
    image = db.Column(db.String(150))


    def __init__(self,username,email,password,bio,image):
        self.email = email
        self.username = username
        self.password = password
        self.bio = bio  
        self.image = image

class Follower(db.Model):
    id = db.Column(db.Integer,primary_key=True,unique=True, nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    follow_id = db.Column(db.Integer,db.ForeignKey('user.id'))   
     
    def __init__(self,user_id,follow_id):
       self.user_id=user_id
       self.follow_id=follow_id

class Pokemon(db.Model):
    id = db.Column(db.Integer,primary_key=True,unique=True, nullable=False)
    name = db.Column(db.String(30),unique=True, nullable=False)
    sprite = db.Column(db.String(100))
    description = db.Column(db.String)
    createdAt = db.Column(db.String)
    updatedAt = db.Column(db.String)
    favorited = db.Column(db.String)
    favoritesCount = db.Column(db.Integer) 
    trainer=db.Column(db.String)

    def __init__(self,name,sprite,description,createdAt,updatedAt,favorited,favoritesCount,trainer):
        self.name=name
        self.sprite=sprite
        self.description=description
        self.createdAt=createdAt
        self.updatedAt=updatedAt
        self.favorited=favorited
        self.favoritesCount=favoritesCount
        self.trainer=trainer

class Taglist(db.Model):
    id = db.Column(db.Integer,primary_key=True,unique=True, nullable=False)
    pokemon_id = db.Column(db.Integer)
    tag = db.Column(db.String)

    def __init__(self,pokemon_id,tag):
        self.pokemon_id=pokemon_id
        self.tag=tag

class Comment(db.Model):
    id = db.Column(db.Integer,primary_key=True,unique=True, nullable=False)
    createdAt = db.Column(db.String)
    updatedAt = db.Column(db.String)
    body = db.Column(db.String)
    trainer=db.Column(db.String)
    pokemon=db.Column(db.String)

    def __init__(self,createdAt,updatedAt,body,trainer,pokemon):
        self.createdAt=createdAt
        self.updatedAt=updatedAt
        self.body=body
        self.trainer=trainer
        self.pokemon=pokemon

class Favorite(db.Model):
    id = db.Column(db.Integer,primary_key=True,unique=True, nullable=False)
    user_id=db.Column(db.Integer)
    fav_pokemon=db.Column(db.Integer)

    def __init__(self,user_id,fav_pokemon):
        self.user_id=user_id
        self.fav_pokemon=fav_pokemon

@app.errorhandler(404)
def page_not_found(error=None):
    return ("Error 404"), 404

@app.errorhandler(500)
def page_not_found_500(e):
    return render_template("404.html"), 404

@app.route("/api/users", methods=["POST"])
def user_reg():
    user=request.json["user"]
    email=user["email"]
    username=user["username"]
    password=user["password"]

    if "bio" in user:
        bio=user["bio"]
    else:
        bio=None
    
    if "image" in user:
        image=user["image"]
    else:
        image=None

    new_user=User(username,email,password,bio,image)

    db.session.add(new_user)
    db.session.commit()

    user=User.query.filter(User.username==username).first()
    new_user={
        "user":{
            "username":user.username,
            "email":user.email,
            "bio":user.bio,
            "image":user.image
        }
    }
    return json.dumps(new_user)

@app.route("/api/users/login",methods=["POST"])
def user_login():
    user=request.json["user"]
    email=user["email"]
    password=user["password"] 

    userdb = User.query.filter(User.email == email).first()

    if email == userdb.email and password==userdb.password : 
        log_user={
        "user":{
            "username":userdb.username,
            "token":create_jwt(identity=userdb.email),
            "email":userdb.email,
            "bio":userdb.bio,
            "image":userdb.image
        }
    }
        
        return jsonify(log_user)
    else:
        return "Unsuccessfull Login" ,401

    

@app.route("/api/user",methods=["GET"])
@jwt_required
def user_get():
    email=get_jwt_identity()
    userdb = User.query.filter(User.email == email).first()
    cur_user={
       "user":{
            "username":userdb.username,
            "token":create_jwt(identity=userdb.email),
            "email":userdb.email,
            "bio":userdb.bio,
            "image":userdb.image
        }
    }

    return jsonify(cur_user)

@app.route("/api/user",methods=["PATCH"])
@jwt_required
def user_update():
    email=get_jwt_identity()
    userdb = User.query.filter(User.email == email).first()
    user=request.json["user"]

    if "email" in user:
        email=user["email"]
        return "Cannot change email",401
    
    if "bio" in user:
        userdb.bio=user["bio"]
    
    if "image" in user:
        userdb.image=user["image"]
    
    if "username" in user:
        userdb.username=user["username"]

    if "password" in user:
        userdb.password=user["password"]

    db.session.commit()

    updated_user={
        "user":{
            "email":userdb.email,
            "username":userdb.username,
            "token":create_jwt(identity=userdb.email),
            "bio":userdb.bio,
            "image":userdb.image
        }
    }

    return json.dumps(updated_user)

@app.route("/api/profiles/<username>",methods=["GET"])
@jwt_required
def get_profile(username):
    userdb = User.query.filter(User.username == username).first()
    cur_user=get_jwt_identity()
    cur_userdb=User.query.filter(User.email == cur_user).first()

    ret={
        "profile":{
            "username":userdb.username,
            "bio":userdb.bio,
            "image":userdb.image,
            "following":Follower.query.filter(Follower.user_id == cur_userdb.id and Follower.follow_id==userdb.id).count()>0
        }
    }
    
    return json.dumps(ret)

@app.route("/api/profiles/<username>/follow",methods=["POST"])
@jwt_required
def follow_user(username):
    userdb = User.query.filter(User.username == username).first()
    cur_user=get_jwt_identity()
    cur_userdb=User.query.filter(User.email == cur_user).first()
    follow_id=userdb.id
    user_id=cur_userdb.id

    #followerdb = Follower.query.filter(Follower.user_id == user_id).first()

    if (Follower.query.filter(Follower.user_id == cur_userdb.id and Follower.follow_id==userdb.id).count()>0) == True  :
        return "You are already following :)",401

    follow_add=Follower(user_id,follow_id)
    db.session.add(follow_add)
    db.session.commit()
    


    ret={
        "profile":{
            "username":userdb.username,
            "bio":userdb.bio,
            "image":userdb.image,
            "following":Follower.query.filter(Follower.user_id == cur_userdb.id and Follower.follow_id==userdb.id).count()>0
        }
    }

    return json.dumps(ret)

@app.route("/api/profiles/<username>/follow",methods=["DELETE"])
@jwt_required
def unfollow_user(username):
    userdb = User.query.filter(User.username == username).first()
    cur_user=get_jwt_identity()
    cur_userdb=User.query.filter(User.email == cur_user).first()
    follow_id=userdb.id
    user_id=cur_userdb.id

    if (Follower.query.filter(Follower.user_id == userdb.id and Follower.follow_id==cur_userdb.id).count()>0) == False:
        return "You are not following ;)",401

    unfollow=Follower.query.filter(Follower.user_id == userdb.id and Follower.follow_id == cur_userdb.id).first()
    
    db.session.delete(unfollow)
    db.session.commit()

    ret={
        "profile":{
            "username":userdb.username,
            "bio":userdb.bio,
            "image":userdb.image,
            "following":Follower.query.filter(Follower.user_id == userdb.id and Follower.follow_id==cur_userdb.id).count()>0
        }
    }

    return json.dumps(ret)

@app.route("/api/pokemon",methods=["POST"])
@jwt_required
def create_pokemon():
    cur_user=get_jwt_identity()
    pokemon=request.json["pokemon"]
    name=pokemon["name"]
    sprite=pokemon["sprite"]
    description=pokemon["description"]
   
    #if "taglist" in pokemon:
    tags=pokemon["tagList"]
    #else:
       # taglist=None

    
    favorited=False
    
    favoritesCount=0;

    createdAt=str(datetime.datetime.now())
    updatedAt=str(datetime.datetime.now())
   
    trainerdb=User.query.filter(User.email == cur_user).first()
    trainer=trainerdb.id

    new_pokemon = Pokemon(name,sprite,description,createdAt,updatedAt,favorited,favoritesCount,trainer)
    
    db.session.add(new_pokemon)
    db.session.commit()

    pokemon = Pokemon.query.filter(Pokemon.name == name).first()
    trainer1=User.query.filter(User.id == trainer).first()

    for tag in tags:
        pokemon_id=pokemon.id
        lists=Taglist(pokemon_id,tag)
        db.session.add(lists)
        db.session.commit()

    tag_data = Taglist.query.filter(pokemon.id==Taglist.pokemon_id).all()

    new_pokemon={
        "Pokemon":{
            "id": pokemon.id,
            "name": pokemon.name,
            "sprite": pokemon.sprite,
            "description": pokemon.description,
            "tagList": [
                t.tag
                for t in tag_data
            ],
            "createdAt": str(pokemon.createdAt),
            "updatedAt": str(pokemon.updatedAt),
            "favorited": "False",#pokemon.favorited,
            "favoritesCount": 0,
            "trainer": {
            "username": trainer1.username,
            "bio": trainer1.bio,
            "image": trainer1.image,
            "following": "False"#Follower.query.filter(Follower.user_id == cur_userdb.id and Follower.follow_id==userdb.id).count()>0
            }
        }
    }

    return jsonify(new_pokemon)

@app.route("/api/pokemon/<name>",methods=["GET"])
@jwt_required
def get_pokemon(name):
    cur_user=get_jwt_identity()
    trainerdb=User.query.filter(User.email == cur_user).first()
    trainer=trainerdb.id
    trainer1=User.query.filter(User.id == trainer).first()
    pokemon = Pokemon.query.filter(Pokemon.name == name).first()
    trainer=User.query.filter(Pokemon.trainer == trainer1.id).first()

    tag_data = Taglist.query.filter(pokemon.id==Taglist.id).all()
    
    pokemon_tag=[]
    for tag_data in tag_data:
        pokemon_tag.append(tag_data.tag)

    get_pokemon={
        "Pokemon":{
            "id": pokemon.id,
            "name": pokemon.name,
            "sprite": pokemon.sprite,
            "description": pokemon.description,
            "tagList": pokemon_tag,
            
            "createdAt": str(pokemon.createdAt),
            "updatedAt": str(pokemon.updatedAt),
            #"favorited":Favorite.query.filter(Favorite.user_id == 1'''trainerdb.id''' and Favorite.fav_pokemon == pokemon.name).count()>0,
            "favoritesCount": Favorite.query.filter(Favorite.user_id==pokemon.id).count(),
            "trainer": {
            "username": trainer.username,
            "bio": trainer.bio,
            "image": trainer.image,
            #"following": Follower.query.filter(Follower.user_id == cur_userdb.id and Follower.follow_id==userdb.id).count()>0
            }
        }
    }

    return jsonify(get_pokemon)

@app.route("/api/pokemon/<name>",methods=["PATCH"])
def update_pokemon(name):
    trainer1=get_jwt_identity()
    pokemon=request.json["pokemon"]

    trainerdb = User.query.filter(User.email==trainer1).first()
    pokemondb = Pokemon.query.filter(Pokemon.name == name).first()
    #trainer=User.query.filter(User.trainer == trainerdb.id).first()

    if "sprite" in pokemon:
        pokemondb.sprite=pokemon["sprite"]
    
    if "description" in pokemon:
        pokemondb.description=pokemon["description"]

    db.session.commit()

    if "tagList" in pokemon:
        for tag in tags:
            pokemon_id=pokemon.id
            lists=Taglist(pokemon_id,tag)
            db.session.add(lists)
            db.session.commit()

    tag_data = Taglist.query.filter(pokemondb.id==Taglist.pokemon_id).all()
    pokemon_tag=[]
        
    for tag_data in tag_data:
        pokemon_tag.append(tag_data.tag)

   

    updated_pokemon={
        "Pokemon":{
            "id": pokemondb.id,
            "name": pokemondb.name,
            "sprite": pokemondb.sprite,
            "description": pokemondb.description,
            "tagList": pokemon_tag,
            "createdAt": str(pokemondb.createdAt),
            "updatedAt": str(pokemondb.updatedAt),
            "favorited": pokemondb.favorited,
            "favoritesCount": Favorite.query.filter(Favorite.user_id==pokemondb.id).count(),
            "trainer": {
            "username": trainerdb.username,
            "bio": trainerdb.bio,
            "image": trainerdb.image,
            "following": Follower.query.filter(Follower.user_id == trainerdb.id and Follower.follow_id==pokemondb.trainer).count()>0
            }
        }
    }
    return jsonify(updated_pokemon)

#Completed till here

@app.route("/api/pokemon/<name>",methods=["DELETE"])
@jwt_required
def delete_pokemon(name):
    trainer1=get_jwt_identity()
    pokemon=request.json["pokemon"]

    trainerdb = User.query.filter(User.email==trainer1).first()
    pokemondb = Pokemon.query.filter(Pokemon.name == name).first()

    '''if "tagList" in pokemon:
        for tag in tags:
            pokemon_id=pokemon.id
            lists=Taglist(pokemon_id,tag)
            db.session.add(lists)
            db.session.commit()'''

    tag_data = Taglist.query.filter(pokemondb.id==Taglist.pokemon_id).all()
    pokemon_tag=[]
        
    for tag_data in tag_data:
        pokemon_tag.append(tag_data.tag)

    deleted_pokemon={
        "Pokemon":{
            "id": pokemondb.id,
            "name": pokemondb.name,
            "sprite": pokemondb.sprite,
            "description": pokemondb.description,
            "tagList": pokemon_tag,
            "createdAt": str(pokemondb.createdAt),
            "updatedAt": str(pokemondb.updatedAt),
            "favorited": pokemondb.favorited,
            "favoritesCount": Favorite.query.filter(Favorite.user_id==pokemondb.id).count(),
            "trainer": {
            "username": trainerdb.username,
            "bio": trainerdb.bio,
            "image": trainerdb.image,
            "following": Follower.query.filter(Follower.user_id == trainerdb.id and Follower.follow_id==pokemondb.trainer).count()>0
            }
        }
    }

    db.session.delete(pokemondb)
    db.session.commit()
    return jsonify(deleted_pokemon)
#Completed till here
                                                                                                       
@app.route("/api/pokemon/<name>/comments",methods=["POST"])
@jwt_required
def add_comment(name):
    trainer=get_jwt_identity()
    comment=request.json["comment"]
    body=comment["body"]

    createdAt=str(datetime.datetime.now())
    updatedAt=str(datetime.datetime.now())
    pokemon=name
    cur_comment=Comment(createdAt,updatedAt,body,trainer,pokemon)
    db.session.add(cur_comment)
    db.session.commit()
    trainerdb=User.query.filter(User.email == trainer).first()


    comment1 = Comment.query.filter(Comment.trainer == trainer).first()
    cur_comment={
        "comment":{
        "id":comment1.id,
        "createdAt":str(comment1.createdAt),
        "updatedAt":str(comment1.updatedAt),
        "body":comment1.body,
        "trainer":{
            "username":trainerdb.username,
            "bio":trainerdb.bio,
            "image":trainerdb.image,
            "following":Follower.query.filter(Follower.user_id == trainerdb.id and Follower.follow_id==pokemondb.trainer).count()>0
        }
        }
    }

    return json.dumps(cur_comment)
#Completed till here

@app.route("/api/pokemon/<name>/comments/<int:id>",methods=["DELETE"])
@jwt_required
def del_comment(name,id):
    comment = Comment.query.filter(Comment.id == id).first()
    db.session.delete(comment)
    db.session.commit()

    return "Comment Deleted"

@app.route("/api/pokemon/<name>/comments",methods=["GET"])
@jwt_required
def get_comment(name):
    trainer=get_jwt_identity()
    trainerdb=User.query.filter(User.email == trainer).first()
    comments1=Comment.query.filter(Comment.pokemon==name).all()
    cur_comment={
        "comments":[{
        "id":comment1.id,
        "createdAt":str(comment1.createdAt),
        "updatedAt":str(comment1.updatedAt),
        "body":comment1.body,
        "trainer":{
            "username":trainerdb.username,
            "bio":trainerdb.bio,
            "image":trainerdb.image,
            "following":Follower.query.filter(Follower.user_id == trainerdb.id and Follower.follow_id==pokemondb.trainer).count()>0
            }
        }
        for comment1 in comments1
        ]
    }

    return jsonify(cur_comment)



@app.route("/api/pokemon/<name>/favorite",methods=["POST"])
@jwt_required
def favorite_pokemon(name):
    cur_user = get_jwt_identity()
    userdb = User.query.filter(User.email == cur_user).first()
    user_id = userdb.id
    fav_pokemon=name
    favpok=Favorite(user_id,fav_pokemon)
    db.session.add(favpok)
    db.session.commit()
    pokemondb = Pokemon.query.filter(Pokemon.name == name).first()

    tag_data = Taglist.query.filter(pokemondb.id==Taglist.pokemon_id).all()
    pokemon_tag=[]
        
    for tag_data in tag_data:
        pokemon_tag.append(tag_data.tag)

    ret={
        "Pokemon":{
            "id": pokemondb.id,
            "name": pokemondb.name,
            "sprite": pokemondb.sprite,
            "description": pokemondb.description,
            "tagList": pokemon_tag,
            "createdAt": str(pokemondb.createdAt),
            "updatedAt": str(pokemondb.updatedAt),
            "favorited": pokemondb.favorited,
            "favoritesCount": 0,
            "trainer": {
            "username": userdb.username,
            "bio": userdb.bio,
            "image": userdb.image,
            "following": Follower.query.filter(Follower.user_id == userdb.id and Follower.follow_id==userdb.id).count()>0
           }
        }
    }    

    return json.dumps(ret)

@app.route("/api/pokemon/<name>/favorite",methods=["DELETE"])
@jwt_required
def unfavorite_pokemon(name):
    cur_user = get_jwt_identity()
    cur_userdb = User.query.filter(User.email == cur_user).first()
    userid = cur_userdb.id
    fav_pokemon=name
    pokemondb = Pokemon.query.filter(Pokemon.name == name).first()
    favpok=Favorite.query.filter(Favorite.user_id==pokemondb.id).first()
    db.session.delete(favpok)
    db.session.commit()

    tag_data = Taglist.query.filter(pokemondb.id==Taglist.pokemon_id).all()
    pokemon_tag=[]
        
    for tag_data in tag_data:
        pokemon_tag.append(tag_data.tag)


    ret={
        "Pokemon":{
            "id": pokemondb.id,
            "name": pokemondb.name,
            "sprite": pokemondb.sprite,
            "description": pokemondb.description,
            "tagList": pokemon_tag,
            "createdAt": str(pokemondb.createdAt),
            "updatedAt": str(pokemondb.updatedAt),
            "favorited": Favorite.query.filter(Favorite.user_id == cur_userdb.id and Favorite.fav_pokemon == pokemondb.name).count()>0,
            "favoritesCount": Favorite.query.filter(Favorite.user_id==pokemondb.id).count(),
            "trainer": {
            "username": cur_userdb.username,
            "bio": cur_userdb.bio,
            "image": cur_userdb.image,
            "following": Follower.query.filter(Follower.user_id == cur_userdb.id and Follower.follow_id==cur_userdb.id).count()>0
           }
        }
    }    

    
  

    return jsonify(ret)

@app.route('/api/tags',methods=['GET'])
def tags():
    tags=db.session.query(Taglist.tag).distinct().all()
    tagslist={
        "tags":
        [
            tag.tag
        for tag in tags
        ]
    }
    return jsonify(tagslist)

#Completed till here

@app.route("/api/pokemon",methods=["GET"])

def list_pokemon():
    limit = request.args.get('limit')
    tag = request.args.get('tag')
    trainer = request.args.get('trainer')
    favorited = request.args.get('favorited')
    offsetlimit = request.args.get('offsetlimit')

    limitdata=[]
    trainerdata=[]
    favoriteddata=[]
    tagdata=[]
    offsetlimitdata=[]
    pokdat=[]
    pokelist=[]

    if limit is None:
        limit=20
    if offsetlimit is None:
        offset=0

    if tag is not None:
        temp=Taglist.query.filter(Taglist.tag==tag).all()
        for i in temp:
            pokelist.append(i.pokemon_id)

    if trainer is not None:
        trainerdb=User.query.filter(User.username==trainer).first()
        trainer_id=trainerdb.id
        temp=Pokemon.query.filter(Pokemon.trainer==trainer_id).all()
        for i in temp:
            pokelist.append(i.id)
    
    if favorited is not None:
        favdb=User.query.filter(User.username==favorited).first()
        fav_id=favdb.id
        temp=Favorite.query.filter(Favorite.user_id==fav_id).all()
        for i in temp:
            pokelist.append(i.fav_pokemon)
    pokelist=list(set(pokelist))
    if(len(pokelist)==0 ):
        all_pokemons=Pokemon.query.order_by(Pokemon.updatedAt.desc()).offset(offset).limit(limit).all()
        all_pokemons=list(all_pokemons)
    else:
        all_pokemons = Pokemon.query.filter(Pokemon.id.in_(pokelist)).order_by(Pokemon.updatedAt.desc()).offset(offset).limit(limit).all()

    for pokemon in all_pokemons:
        tag_data = Taglist.query.filter(pokemon.id==Taglist.id).all()
        
        pokemon_tag=[]
        for tag_data in tag_data:
            pokemon_tag.append(tag_data.tag)
        trainer_data=User.query.get(pokemon.trainer)
        pokemondata={
                "id": pokemon.id,
                "name": pokemon.name,
                "sprite": pokemon.sprite,
                "description": pokemon.description,
                "tagList":  pokemon_tag,
                "createdAt": str(pokemon.createdAt),
                "updatedAt": str(pokemon.updatedAt),
                "favorited": False,
                "favoritesCount": Favorite.query.filter(Favorite.user_id==pokemon.id).count(),
                "trainer": {
                "username": trainer_data.username,
                "bio": trainer_data.bio,
                "image": trainer_data.image,
                "following": False #Follower.query.filter(Follower.user_id == trainerdb.id and Follower.follow_id==pokemondb.trainer).count()>0
                }
            }
        
    pokdat.append(pokemondata)

    return jsonify({"pokemons":pokdat,"pokemon_count":len(pokdat)})
 # Run Server
if __name__ == "__main__":
    db.create_all()
    app.run(host="localhost", debug=True, port=8006)