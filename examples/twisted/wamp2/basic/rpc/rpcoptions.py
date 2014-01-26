###############################################################################
##
##  Copyright (C) 2014 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks

from autobahn.wamp.protocol import WampAppSession
from autobahn.wamp.types import CallOptions, RegisterOptions, PublishOptions



class RpcOptionsBackend(WampAppSession):
   """
   An application component providing procedures with
   different kinds of arguments.
   """

   def onSessionOpen(self, details):

      def square(val, details = None):
         print("square called from: {}".format(details.caller))

         if val < 0:
            self.publish('com.myapp.square_on_nonpositive', val)
         elif val == 0:
            self.publish('com.myapp.square_on_nonpositive', val, 
               options = PublishOptions(exclude = [details.caller]))
         return val * val

      self.register(square, 'com.myapp.square', RegisterOptions(details_arg = 'details'))



class RpcOptionsFrontend(WampAppSession):
   """
   An application component calling the different backend procedures.
   """

   @inlineCallbacks
   def onSessionOpen(self, info):

      def on_event(val):
         print("Someone requested to square non-negative: {}".format(val))

      yield self.subscribe(on_event, 'com.myapp.square_on_nonpositive')

      for val in [2, 0, -2]:
         res = yield self.call('com.myapp.square', val, options = CallOptions(discloseMe = True))
         print("Squared {} = {}".format(val, res))

      self.closeSession()


   def onSessionClose(self, details):
      reactor.stop()
