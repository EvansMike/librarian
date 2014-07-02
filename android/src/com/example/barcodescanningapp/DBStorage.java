/*
 * DBStorage.java
 * 
 * Copyright 2014 mikee <mikee@thinky.saxicola>
 * 
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 * MA 02110-1301, USA.
 * 
 * Store into librarian DB if available, else temporary store on device
 * until we can connect to the librarian DB.
 */
package com.example.barcodescanningapp;

import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.URL;
import java.net.URLConnection;

import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.StatusLine;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.DefaultHttpClient;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import android.net.Uri;
import android.os.AsyncTask;
import android.os.Bundle;
import android.app.Activity;
import android.content.Intent;
import android.widget.Toast;
import android.util.Log;
import android.content.Context;

import android.content.ContentValues;
import android.database.sqlite.SQLiteCursor;

import com.example.barcodescanningapp.MySQLiteHelper;
import android.database.sqlite.SQLiteDatabase;
import android.database.Cursor;

public class DBStorage {
    //public static final int DATABASE_VERSION = 2;
    public static final String DATABASE_NAME = "librarian.db";
    private MySQLiteHelper dbHelper; 
    private SQLiteDatabase database;
    private String LIBRARIAN_API = ""; // TODO
    
    // Example code CHANGE ME
    public final static String BOOK_TABLE="books"; // name of table 
  
     
     /** 
         * 
         * @param context 
         */  
        public DBStorage(Context context){
            Log.d("DBStorage","Here we are!");  
            dbHelper = new MySQLiteHelper(context);  
            database = dbHelper.getWritableDatabase();  
        }
        
        public long createRecords(String isbn, String author, String title, String publisher ,
                        String description, String date, String rating)
        {  
           ContentValues values = new ContentValues();  
           values.put("isbn", isbn); 
           values.put("author", author);  
           values.put("title", title);
           values.put("publisher", publisher);
           values.put("description", description);
           values.put("date", date);
           values.put("rating", rating);
           Log.d(DBStorage.class.getName(),author);  
           return database.insert(BOOK_TABLE, null, values);  
        }    
    
    public Cursor selectRecords() {
       String[] cols = new String[] {"isbn, author","title","publisher","description","date","rating"};  
       Cursor mCursor = database.query(BOOK_TABLE,null,null,null, null, null, null);  
       if (mCursor != null) {  
         mCursor.moveToFirst();  
       }  
       return mCursor; // iterate to get each value.
    }
    
    /* Send stored books to the master librarian database.
     * When sent and confirmed empty the local storage.
     */
    public int updateLibrarian()
    {
        // Get data as JSON from database.
        //Log.d("updateLibrarian", "I'm in here now.");
        Cursor mCursor = selectRecords();
        int rowCount = mCursor.getCount(); // Num rows in DB
        JSONObject jsonObject = new JSONObject();
        JSONArray array = new JSONArray();
        while (mCursor.isAfterLast() == false) 
        {
         JSONObject json = new JSONObject();   
         //String item = mCursor.getString(0);
         try{
             json.put("ISBN",mCursor.getString(0));
             json.put("AUTHOR",mCursor.getString(1));
             json.put("TITLE",mCursor.getString(2));
             json.put("PUBLISHER",mCursor.getString(3));
             json.put("DESCRIPTION",mCursor.getString(4));
             json.put("DATE",mCursor.getString(5));
             json.put("RATING",mCursor.getString(6));
             array.put(json);
            }
        catch (JSONException jse){jse.printStackTrace();}
        
        mCursor.moveToNext();   
        }
        mCursor.close();
        try {
            jsonObject.put("BOOK", array);
            Log.d("updateLibrarian",jsonObject.toString(2));
            }
        catch (JSONException jse){jse.printStackTrace();}
        
        // Now send that to the librarian API
        // TODO Write the API.  Oooh, found one already written, partly.
        int result = 0; // Number of rows inserted on server, should match rows sent.
        
        
        
        // Delete all from database once we've uploaded it.
        if (result == rowCount){database.delete(BOOK_TABLE, null, null);}
        return 1; // FIXME
    }
    
    public void sendToAPI(JSONObject json){
        
    }
}
