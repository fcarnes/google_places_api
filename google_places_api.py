#This python script is to query places information (including place name, X/Y coordinates) from users' text/type search using Google Places API.
#The code is using Nearby Search Request for searches for school, hospital, and mosque only.
#The Google Places API Text Search Service returns information about a set of places based on a string (for charitable organizations and house of worship search only) . For example, "restaurants in Boston".
#For mosque,hospital, and school in Egypt, they are searching by Google supported Types(https://developers.google.com/places/documentation/supported_types);
#but for charitable organizations and house of worship, they are searching by text, e.g. charitable+organizations+Egypt.
#Python 2.X

import sys, urllib, urllib2, json, base64, hashlib, hmac, time, unicodedata

#The input file must to be a tab delimited text file with only three columns without headers. The order of the three columns must to be: ID, X, and Y.
#You will need to change the directory (within the double quotation mark below) HERE for the input file
in_request = r".../coordinates.txt"
#You will need to change the directory HERE for the output file
out_return = r".../output.txt"

google_url = "https://maps.googleapis.com"
nearbysearch_endpoint = "/maps/api/place/nearbysearch/json?"

#API Server Key - it is currently based on my computer IP address"
#You will need to login to the Egypt Project Gmail account, add your computer IP address, request for a new API Key, and replace the key - ProjectAPI below. 
ProjectAPI = ""

#Search by types (have to be exactly the name - mosque,police, or church)
#You will have to change the search type if searching for a different type one at a time)
nearby_type = "mosque"

#However, for charitable organizations and house of worship, you will have to search by text instead of types
#text_query = "charitable+organization+Egypt"
#text_query = "house+of+worship+Egypt"


f_in = open(in_request, 'r')
f_out = open(out_return, 'w')
f_out.write("%s\t%s\t%s\t%s\n" % ("ID", "Name", "Latitude","Longitude"))
f_in_line = f_in.readlines()
i = 0
# Setting an initial delay of 0.01 seconds between each requests to allow the default 1000 queries per second limit
Distance_QPS = 0.01
delay = Distance_QPS

for line in f_in_line:
    attempts = 0
    success = False
    fields = line.strip().replace("\"", "").split('\t')
    for field in fields:
        #nearby_search = ''.join(field)
        nearby_search = "%s,%s" % (fields[2], fields[1])
        #nearby_search = unicodedata.normalize('NFKD', nearby_search.decode("utf-8", "replace")).encode('ascii', 'ignore')
        nearby_search = nearby_search.replace("n/a", "").replace(" ", ",")

        # the code line below is to search school, hospital, mosque ( all Google supported Types) only. Please remove the "#"  and add "#" to the next code line to perform this line of code only.
        # if you have questions about "Nearby Search Requests" using Google Places API, please refer to https://developers.google.com/places/webservice/search#PlaceSearchRequests
        # the radius has to be in meters. 750 feet = 228.6 meters

        signedurl = google_url + nearbysearch_endpoint + "location=" + nearby_search + "&radius=228.6"+"&type="+nearby_type+"&key=" + ProjectAPI

        # the code line below is to search charitable organizations, and house of worship only. 
        # In your case, using "Text Search Requests" works better than "Nearby Search Request - search by types", but one single request counts for 10 times against your quota.

        #signedurl = google_url + nearbysearch_endpoint + "location=" + nearby_search + "&radius=7500"+"&query="+text_query+"&key=" + ProjectAPI

        print signedurl

    # no need to change the rest of the code    
    while success != True and attempts <3:
        time.sleep(delay)
        result = urllib.urlopen(signedurl)
        result_json = json.loads(result.read())
        check_status = result_json["status"]
        if check_status == "OK":
            #print len(result_json["results"])
            for i in range(len(result_json["results"])):
                Name = result_json["results"][i]["name"]
                print Name
                #institution name needs to be unicoded and encoded.
                Name1=unicodedata.normalize("NFKD", Name).encode('utf-8', 'ignore')
                #Address = result_json["results"][i]["formatted_address"]
                Lat = result_json["results"][i]["geometry"]["location"]["lat"]
                Lng = result_json["results"][i]["geometry"]["location"]["lng"]
                f_out.write("%s\t%s\t%s\t%s\n" % (fields[0], Name1, Lat, Lng))
                i = i+1
                print "status:%s timestamp:%s ID = %s is processed" % (check_status, time.strftime("%I:%M:%S"), fields[0])
                print " "
                success = True
        elif check_status == "REQUEST_DENIED" or check_status == "INVALID_REQUEST":
            f_out.write("%s\t%s\n" % (fields[0], check_status))
            print "status:%s timestamp:%s ID = %s is malfored, check your URL" % (check_status, time.strftime("%I:%M:%S"), fields[0])
            print " "
            success = True
        elif check_status == "OVER_QUERY_LIMIT":
            print "status:%s timestamp:%s ID = %s cannot be processed" % (check_status, time.strftime("%I:%M:%S"), fields[0])
            print " "
            for i in range(len(result_json["results"])):
                Name = result_json["results"][i]["name"]
                Name1=unicodedata.normalize("NFKD", Name).encode('utf-8', 'ignore')
                Lat = result_json["results"][i]["geometry"]["location"]["lat"]
                Lng = result_json["results"][i]["geometry"]["location"]["lng"]
                f_out.write("%s\t%s\t%s\t%s\n" % (fields[0], Name1, Lat, Lng))
                i = i+1
            #count numbers of consecutive over quota errors
            attempts +=1
            #increase subsequent 0.01 second delay if over quota status is detected
            delay += 0.01
            #implement 2 seconds pause before recalculating distances
            time.sleep (2)
            #retry
            continue
        else:
            print "status:%s timestamp:%s ID = %s returns no result" % (check_status, time.strftime("%I:%M:%S"), fields[0])
            print " "
            f_out.write("%s\t%s\n" % (fields[0],check_status))
            #count number of consecutive unknown errors
            attempts += 1
            success = True
    if attempts == 3:
        break
        print "Daily limit has been reached"

print "Finished!"
print "Process Ends: %s" % time.asctime( time.localtime(time.time()) )
f_in.close()
f_out.close()
