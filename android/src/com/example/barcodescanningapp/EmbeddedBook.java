package com.example.barcodescanningapp;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;


import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebView;

/**class presents book preview to user*/
public class EmbeddedBook extends Activity {

	private WebView embedView;

	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.embedded_book);
		embedView = (WebView)findViewById(R.id.embedded_book_view);
		embedView.getSettings().setJavaScriptEnabled(true);
		Bundle extras = getIntent().getExtras();
		if(extras !=null)
		{
			String isbn = extras.getString("isbn");
			//try to load asset
			try{
				InputStream pageIn = getAssets().open("embedded_book_page.html");
				BufferedReader htmlIn = new BufferedReader(new InputStreamReader(pageIn));
				StringBuilder htmlBuild = new StringBuilder("");

				String lineIn;
				while ((lineIn = htmlIn.readLine()) != null) {
					htmlBuild.append(lineIn);
				}

				htmlIn.close();
				//pass isbn
				String embeddedPage = htmlBuild.toString().replace("$ISBN$", isbn);
				embedView.loadData(embeddedPage, "text/html", "utf-8");
			}
			catch(IOException ioe){
				embedView.loadData
				("<html><head></head><body>Whoops! Something went wrong.</body></html>", 
						"text/html", "utf-8");
				ioe.printStackTrace();
			}
		}

	}
}
