package com.example.barcodescanningapp;

import android.content.Context;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import android.util.Log;

public class MySQLiteHelper extends SQLiteOpenHelper {
    
    private static final String DATABASE_NAME = "DBName";

    private static final int DATABASE_VERSION = 8;
    
    private static final String DATABASE_CREATE = "CREATE TABLE books(" +
            "isbn text primary key, author text, title text, publisher text, description text, date text, rating text);";
        

    public MySQLiteHelper(Context context) {
        super(context, DATABASE_NAME, null, DATABASE_VERSION);
    }

    // Method is called during creation of the database
    @Override
    public void onCreate(SQLiteDatabase database) {
        database.execSQL(DATABASE_CREATE);
    }

    // Method is called during an upgrade of the database,
    @Override
    public void onUpgrade(SQLiteDatabase database,int oldVersion,int newVersion){
        Log.w(MySQLiteHelper.class.getName(),
                         "Upgrading database from version " + oldVersion + " to "
                         + newVersion + ", which will destroy all old data");
        database.execSQL("DROP TABLE IF EXISTS books"); //TODO
        onCreate(database);
    }
 

} 
