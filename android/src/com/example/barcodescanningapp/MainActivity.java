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
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.util.Log;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import com.google.zxing.integration.android.IntentIntegrator;
import com.google.zxing.integration.android.IntentResult;


/**
 * This is demo code to accompany the Mobiletuts+ tutorial series:
 * - Android SDK: Create a Book Scanning App
 * 
 * Sue Smith
 * May/ June 2013
 *
 */
public class MainActivity extends Activity implements OnClickListener {
	String API_KEY = "AIzaSyDP4pNjcWfRWRNZvt1FCZu1vY8I-ehmN5c";
	//scan, preview, link buttons
	private Button scanBtn, previewBtn, linkBtn, saveBtn;
	//author, title, description, date and rating count text views
	private TextView authorText, titleText, descriptionText, dateText, ratingCountText;
	//layout for star rating
	private LinearLayout starLayout;
	//thumbnail
	private ImageView thumbView;
	//star views
	private ImageView[] starViews;
	//thumbnail bitmap
	private Bitmap thumbImg;

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_main);
		//retrieve scan button and listen for clicks
		scanBtn = (Button)findViewById(R.id.scan_button);
		scanBtn.setOnClickListener(this);

		//preview and link buttons
		previewBtn = (Button)findViewById(R.id.preview_btn);
		previewBtn.setVisibility(View.GONE);
		previewBtn.setOnClickListener(this);
		linkBtn = (Button)findViewById(R.id.link_btn);
		linkBtn.setVisibility(View.GONE);
		linkBtn.setOnClickListener(this);
		saveBtn = (Button)findViewById(R.id.save_btn);
		saveBtn.setVisibility(View.GONE);
		saveBtn.setOnClickListener(this);

		//ui items
		authorText = (TextView)findViewById(R.id.book_author);
		titleText = (TextView)findViewById(R.id.book_title);
		descriptionText = (TextView)findViewById(R.id.book_description);
		dateText = (TextView)findViewById(R.id.book_date);
		starLayout = (LinearLayout)findViewById(R.id.star_layout);
		ratingCountText = (TextView)findViewById(R.id.book_rating_count);
		thumbView = (ImageView)findViewById(R.id.thumb);

		//star views
		starViews=new ImageView[5];
		for(int s=0; s<starViews.length; s++){
			starViews[s]=new ImageView(this);
		}

		//retrieve state
		if (savedInstanceState != null){
			authorText.setText(savedInstanceState.getString("author"));
			titleText.setText(savedInstanceState.getString("title"));
			descriptionText.setText(savedInstanceState.getString("description"));
			dateText.setText(savedInstanceState.getString("date"));
			ratingCountText.setText(savedInstanceState.getString("ratings"));
			int numStars = savedInstanceState.getInt("stars");//zero if null
			for(int s=0; s<numStars; s++){
				starViews[s].setImageResource(R.drawable.star);
				starLayout.addView(starViews[s]);
			}
			starLayout.setTag(numStars);
			thumbImg = (Bitmap)savedInstanceState.getParcelable("thumbPic");
			thumbView.setImageBitmap(thumbImg);
			previewBtn.setTag(savedInstanceState.getString("isbn"));//null if not there

			if(savedInstanceState.getBoolean("isEmbed")) previewBtn.setEnabled(true);
			else previewBtn.setEnabled(false);
			if(savedInstanceState.getInt("isLink")==View.VISIBLE) linkBtn.setVisibility(View.VISIBLE);
			else linkBtn.setVisibility(View.GONE);
			saveBtn.setVisibility(View.VISIBLE);
			previewBtn.setVisibility(View.VISIBLE);

		}
	}

	public void onClick(View v){
		//check for scan button
		if(v.getId()==R.id.scan_button){
			//instantiate ZXing integration class
			IntentIntegrator scanIntegrator = new IntentIntegrator(this);
			//start scanning
			scanIntegrator.initiateScan();
		}
		else if(v.getId()==R.id.link_btn){
			//get the url tag
			String tag = (String)v.getTag();
			//launch the url
			Intent webIntent = new Intent(Intent.ACTION_VIEW);
			webIntent.setData(Uri.parse(tag));
			startActivity(webIntent);
		}
		else if(v.getId()==R.id.preview_btn){
			String tag = (String)v.getTag();
			//launch preview
			Intent intent = new Intent(this, EmbeddedBook.class);
			intent.putExtra("isbn", tag);
			startActivity(intent);
		}
	}

	public void onActivityResult(int requestCode, int resultCode, Intent intent) {
		//retrieve result of scanning - instantiate ZXing object
		IntentResult scanningResult = IntentIntegrator.parseActivityResult(requestCode, resultCode, intent);
		//check we have a valid result
		if (scanningResult != null) {
			//get content from Intent Result
			String scanContent = scanningResult.getContents();
			//get format name of data scanned
			String scanFormat = scanningResult.getFormatName();
			Log.v("SCAN", "content: "+scanContent+" - format: "+scanFormat);
			if(scanContent!=null && scanFormat!=null && scanFormat.equalsIgnoreCase("EAN_13")){
				previewBtn.setTag(scanContent);
				String bookSearchString = "https://www.googleapis.com/books/v1/volumes?" +
						"q=isbn:"+scanContent+"&key=" + API_KEY;
				//fetch search results
				new GetBookInfo().execute(bookSearchString);
			}
			else{
				//not ean
				Toast toast = Toast.makeText(getApplicationContext(), 
						"Not a valid scan!", Toast.LENGTH_SHORT);
				toast.show();
			}
		}
		else{
			//invalid scan data or scan canceled
			Toast toast = Toast.makeText(getApplicationContext(), 
					"No book scan data received!", Toast.LENGTH_SHORT);
			toast.show();
		}
	}

	//class to fetch book info
	private class GetBookInfo extends AsyncTask<String, Void, String> {
		@Override
		protected String doInBackground(String... bookURLs) {
			StringBuilder bookBuilder = new StringBuilder();
			for (String bookSearchURL : bookURLs) {
				HttpClient bookClient = new DefaultHttpClient();
				try {
					//get the data
					HttpGet bookGet = new HttpGet(bookSearchURL);
					HttpResponse bookResponse = bookClient.execute(bookGet);
					StatusLine bookSearchStatus = bookResponse.getStatusLine();
					if (bookSearchStatus.getStatusCode()==200) {
						//we have a result
						HttpEntity bookEntity = bookResponse.getEntity();
						InputStream bookContent = bookEntity.getContent();
						InputStreamReader bookInput = new InputStreamReader(bookContent);
						BufferedReader bookReader = new BufferedReader(bookInput);
						String lineIn;
						while ((lineIn=bookReader.readLine())!=null) {
							bookBuilder.append(lineIn);
						}
					}
				}
				catch(Exception e){ 
					e.printStackTrace(); 
				}
			}
			return bookBuilder.toString();
		}
		protected void onPostExecute(String result) {
			try{
				//parse results
				previewBtn.setVisibility(View.VISIBLE);
				JSONObject resultObject = new JSONObject(result);
				JSONArray bookArray = resultObject.getJSONArray("items");
				JSONObject bookObject = bookArray.getJSONObject(0);
				JSONObject volumeObject = bookObject.getJSONObject("volumeInfo");
				//try for title
				try{ titleText.setText("TITLE: "+volumeObject.getString("title")); }
				catch(JSONException jse){ 
					titleText.setText("");
					jse.printStackTrace(); 
				}
				//author can be multiple
				StringBuilder authorBuild = new StringBuilder("");
				try{
					JSONArray authorArray = volumeObject.getJSONArray("authors");
					for(int a=0; a<authorArray.length(); a++){
						if(a>0) authorBuild.append(", ");
						authorBuild.append(authorArray.getString(a));
					}
					authorText.setText("AUTHOR(S): "+authorBuild.toString());
				}
				catch(JSONException jse){ 
					authorText.setText("");
					jse.printStackTrace(); 
				}
				//publication date
				try{ dateText.setText("PUBLISHED: "+volumeObject.getString("publishedDate")); }
				catch(JSONException jse){ 
					dateText.setText("");
					jse.printStackTrace(); 
				}
				//book description
				try{ descriptionText.setText("DESCRIPTION: "+volumeObject.getString("description")); }
				catch(JSONException jse){ 
					descriptionText.setText("");
					jse.printStackTrace(); 
				}
				//star rating display
				try{ 
					double decNumStars = Double.parseDouble(volumeObject.getString("averageRating"));
					int numStars = (int)decNumStars;
					starLayout.setTag(numStars);
					starLayout.removeAllViews();
					for(int s=0; s<numStars; s++){
						starViews[s].setImageResource(R.drawable.star);
						starLayout.addView(starViews[s]);
					}
				}
				catch(JSONException jse){ 
					starLayout.removeAllViews();
					jse.printStackTrace(); 
				}
				//rating count
				try{ ratingCountText.setText(" - "+volumeObject.getString("ratingsCount")+" ratings"); }
				catch(JSONException jse){
					ratingCountText.setText("");
					jse.printStackTrace();
				}
				//preview availability
				try{
					boolean isEmbeddable = Boolean.parseBoolean
							(bookObject.getJSONObject("accessInfo").getString("embeddable"));
					if(isEmbeddable) previewBtn.setEnabled(true);
					else previewBtn.setEnabled(false);
				}
				catch(JSONException jse){ 
					previewBtn.setEnabled(false);
					jse.printStackTrace(); 
				}
				//link button
				try{
					linkBtn.setTag(volumeObject.getString("infoLink"));
					linkBtn.setVisibility(View.VISIBLE);
					saveBtn.setVisibility(View.VISIBLE);
				}
				catch(JSONException jse){ 
					linkBtn.setVisibility(View.GONE);
					jse.printStackTrace(); 
				}
				//image thumbnail
				try{ 
					JSONObject imageInfo = volumeObject.getJSONObject("imageLinks");
					new GetBookThumb().execute(imageInfo.getString("smallThumbnail"));
				}
				catch(JSONException jse){ 
					thumbView.setImageBitmap(null);
					jse.printStackTrace();
				}
			}
			catch (Exception e) {
				//no result
				e.printStackTrace();
				titleText.setText("NOT FOUND");
				authorText.setText("");
				descriptionText.setText("");
				dateText.setText("");
				starLayout.removeAllViews();
				ratingCountText.setText("");
				thumbView.setImageBitmap(null);
				previewBtn.setVisibility(View.GONE);
			}
		}
	}

	//class to fetch thumbnail
	private class GetBookThumb extends AsyncTask<String, Void, String> {
		@Override
		protected String doInBackground(String... thumbURLs) {
			try{
				//attempt to download thumbnail image using passed URL
				URL thumbURL = new URL(thumbURLs[0]);
				URLConnection thumbConn = thumbURL.openConnection(); 
				thumbConn.connect(); 
				InputStream thumbIn = thumbConn.getInputStream(); 
				BufferedInputStream thumbBuff = new BufferedInputStream(thumbIn); 
				thumbImg = BitmapFactory.decodeStream(thumbBuff);

				thumbBuff.close(); 
				thumbIn.close(); 
			}
			catch(Exception e) {
				e.printStackTrace();
			}
			return "";
		}
		protected void onPostExecute(String result) {
			//show the image
			thumbView.setImageBitmap(thumbImg);
		}
	}
	//save state
	protected void onSaveInstanceState(Bundle savedBundle) {
		savedBundle.putString("title", ""+titleText.getText());
		savedBundle.putString("author", ""+authorText.getText());
		savedBundle.putString("description", ""+descriptionText.getText());
		savedBundle.putString("date", ""+dateText.getText());
		savedBundle.putString("ratings", ""+ratingCountText.getText());
		savedBundle.putParcelable("thumbPic", thumbImg);
		if(starLayout.getTag()!=null)
			savedBundle.putInt("stars", Integer.parseInt(starLayout.getTag().toString()));
		savedBundle.putBoolean("isEmbed", previewBtn.isEnabled());
		savedBundle.putInt("isLink", linkBtn.getVisibility());
		if(previewBtn.getTag()!=null)
			savedBundle.putString("isbn", previewBtn.getTag().toString());
	}
}
