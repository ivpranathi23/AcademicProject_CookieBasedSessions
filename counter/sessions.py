"""
Project : Project3
File Name: sessions.py
Author: Venkata Pranathi Immaneni
Date: 21st Oct 2020
Email: ivpranathi@csu.fullerton.edu

"""
import logging
import uuid

from flask.sessions import SessionInterface, SessionMixin
from werkzeug.datastructures import CallbackDict
import requests


class SessionStore:

    def __init__(self, logger=None):
        if logger is None:
            self.logger = logging.getLogger("__name__")
        else:
            self.logger = logger

    def set_key(self, key, value):
        self.logger.debug("set_key('%s', '%s')", key, value)
        raise NotImplementedError()

    def get_key(self, key):
        self.logger.debug("get_key('%s')", key)
        raise NotImplementedError()

    def delete_key(self, key):
        self.logger.debug("delete_key('%s')", key)
        raise NotImplementedError()


class KeyValueSessionStore(SessionStore):

    def __init__(self, url, logger=None):
        super().__init__(logger)
        
    def set_key(self, key, value):
    
    	#Creating a dictionary to pass key and value as JSON to the post method
    	dict = {key: value}
    	
    	#Setting the headers to send in the request
    	setHeaders = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    	
    	#POST Request to kv.py. Key is the session Id and value will be the counter
    	return requests.post('http://localhost:5100/', json=dict, headers=setHeaders) 
    
    def delete_key(self, key):
    	#DELETE request to kv.py to delete the specified key
    	return requests.delete("http://localhost:5100/"+key)
    	
    def get_key(self, key):
    	
    	#GET request to kv.py by passing the key.
        res = requests.get("http://localhost:5100/"+key)
        #Retrieving the counter of the specified key
        return res.json().get(key)
    	
class ServerSideSession(CallbackDict, SessionMixin):

    def __init__(self, initial=None, sid=None):

        def on_update(self):
            self.modified = True

        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.modified = False


class ServerSideSessionInterface(SessionInterface):

    def __init__(self, session_store):
        self.session_store = session_store

    def _update_session(self, app, session, response):
        self.session_store.set_key(session.sid, dict(session))
        response.set_cookie(
            app.session_cookie_name,
            session.sid,
            expires=self.get_expiration_time(app, session),
            httponly=self.get_cookie_httponly(app),
            domain=self.get_cookie_domain(app),
            path=self.get_cookie_path(app),
            secure=self.get_cookie_secure(app)
        )

    def _delete_session(self, app, response, sid):
        response.delete_cookie(
            app.session_cookie_name,
            domain=self.get_cookie_domain(app),
            path=self.get_cookie_path(app)
        )
        self.session_store.delete_key(sid)

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if not sid:
            # Create a session object with a new session id
            sid = str(uuid.uuid4())
            return ServerSideSession(sid=sid)

	
        data = self.session_store.get_key(sid)

        if data:
            # Create a session object with existing data
            return ServerSideSession(data, sid=sid)

        # create an empty session object
        return ServerSideSession(sid=sid)

    def save_session(self, app, session, response):

        if not session:
            if session.modified:
                self._delete_session(app, response, session.sid)
            return

        if self.should_set_cookie(app, session):
            self._update_session(app, session, response)
