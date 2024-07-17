
using System;
using System.Net.Http;
using System.Threading.Tasks;
using System.Text;
using System.Web;
using System.Text.Json;

// MAIN
namespace REST{
    class Program{
        // REST GET Over HTTPS - AWS Endpoint
        static async Task<string> rest_get_aws(string table, string acct, string dev){
            // Initialize return string
            string output;

            // Initialize HTTPClient
            HttpClient client = new HttpClient();

            // Build URL with query string
            string host_path = "https://tg0crx57g5.execute-api.us-east-2.amazonaws.com/a2b/app";
            //string url = host_path + "?table=" + table + "&acct=" + acct + "&dev=" + dev;

            // Build URI with query string
            var builder = new UriBuilder(host_path);
            builder.Port = -1;
            var query = HttpUtility.ParseQueryString(builder.Query);
            query["table"] = table;
            query["acct"] = acct;
            query["dev"] = dev;
            builder.Query = query.ToString();
            string url = builder.ToString();

            // Try making the request
            try{
                HttpResponseMessage response = await client.GetAsync(url);
                response.EnsureSuccessStatusCode();
                string responseBody = await response.Content.ReadAsStringAsync();
                output = responseBody;
            }
            catch(HttpRequestException e){
                string error = "\nException Caught! Message: " + e.Message;
                output = error;
            }

            // Return from Task
            return await Task.FromResult(output);
        }

        // REST PUT Over HTTPS - AWS Endpoint
        static async Task<string> rest_put_aws(string table, string data){
            // Initialize return string & HTTP Content
            string output;
            var content = new StringContent(data, Encoding.UTF8, "application/json");

            // Initialize HTTPClient
            HttpClient client = new HttpClient();

            // Build URL with query string
            string host_path = "https://tg0crx57g5.execute-api.us-east-2.amazonaws.com/a2b/app";
            //string url = host_path + "?table=" + table;

            // Build URI with query string
            var builder = new UriBuilder(host_path);
            builder.Port = -1;
            var query = HttpUtility.ParseQueryString(builder.Query);
            query["table"] = table;
            builder.Query = query.ToString();
            string url = builder.ToString();

            // Try making the request
            try{
                HttpResponseMessage response = await client.PutAsync(url, content);
                response.EnsureSuccessStatusCode();
                string responseBody = await response.Content.ReadAsStringAsync();
                output = responseBody;
            }
            catch(HttpRequestException e){
                string error = "\nException Caught! Message: " + e.Message;
                output = error;
            }

            // Return from Task
            return await Task.FromResult(output);
        }

        // REST PUT Over HTTPS - AWS Endpoint
        static async Task<string> rest_del_aws(string acct, string dev, string flag){
            // Initialize return string
            string output;

            // Initialize HTTPClient
            HttpClient client = new HttpClient();

            // Build URL with query string
            string host_path = "https://tg0crx57g5.execute-api.us-east-2.amazonaws.com/a2b/app";
            //string url = host_path + "?acct=" + acct + "&dev=" + dev + "&flag=" + flag;

            // Build URI with query string
            var builder = new UriBuilder(host_path);
            builder.Port = -1;
            var query = HttpUtility.ParseQueryString(builder.Query);
            query["acct"] = acct;
            query["dev"] = dev;
            query["flag"] = flag;
            builder.Query = query.ToString();
            string url = builder.ToString();

            // Try making the request
            try{
                HttpResponseMessage response = await client.DeleteAsync(url);
                response.EnsureSuccessStatusCode();
                string responseBody = await response.Content.ReadAsStringAsync();
                output = responseBody;
            }
            catch(HttpRequestException e){
                string error = "\nException Caught! Message: " + e.Message;
                output = error;
            }

            // Return from Task
            return await Task.FromResult(output);
        }

        // REST GET Over HTTPS - Device Endpoint
        static async Task<string> rest_get_dev(string table){
            // Initialize return string
            string output;

            // Initialize HTTPClient
            HttpClient client = new HttpClient();

            // Build a URI for connected smart devices using their universal hostname
            //string host_path = "http://vsp-esp32";
            string host_path = "http://192.168.4.1";
            //string url = host_path + "?table=" + table + "&src=app";

            // Build URI with query string
            var builder = new UriBuilder(host_path);
            builder.Port = -1;
            var query = HttpUtility.ParseQueryString(builder.Query);
            query["table"] = table;
            query["src"] = "app";
            builder.Query = query.ToString();
            string url = builder.ToString();

            // Try making the request
            try{
                HttpResponseMessage response = await client.GetAsync(url);
                response.EnsureSuccessStatusCode();
                string responseBody = await response.Content.ReadAsStringAsync();
                output = responseBody;
            }
            catch(HttpRequestException e){
                string error = "\nException Caught! Message: " + e.Message;
                output = error;
            }

            // Return from Task
            return await Task.FromResult(output);
        }

        // REST PUT Over HTTPS - Device Endpoint
        static async Task<string> rest_put_dev(string table, string data){
            // Initialize return string & HTTP Content
            string output;
            var content = new StringContent(data, Encoding.UTF8, "application/json");

            // Initialize HTTPClient
            HttpClient client = new HttpClient();

            // Build a URI for connected smart devices using their universal hostname
            //string host_path = "http://vsp-esp32";
            string host_path = "http://192.168.4.1";
            //string url = host_path + "?table=" + table + "&src=app";

            // Build URI with query string
            var builder = new UriBuilder(host_path);
            builder.Port = -1;
            var query = HttpUtility.ParseQueryString(builder.Query);
            query["table"] = table;
            query["src"] = "app";
            builder.Query = query.ToString();
            string url = builder.ToString();

            // Try making the request
            try{
                HttpResponseMessage response = await client.PutAsync(url, content);
                response.EnsureSuccessStatusCode();
                string responseBody = await response.Content.ReadAsStringAsync();
                output = responseBody;
            }
            catch(HttpRequestException e){
                string error = "\nException Caught! Message: " + e.Message;
                output = error;
            }

            // Return from Task
            return await Task.FromResult(output);
        }

        // REST PUT Over HTTPS - Device Endpoint
        static async Task<string> rest_del_dev(){
            // Initialize return string
            string output;

            // Initialize HTTPClient
            HttpClient client = new HttpClient();

            // Build a URI for connected smart devices using their universal hostname
            //string host_path = "http://vsp-esp32";
            string host_path = "http://192.168.4.1";
            //string url = host_path + "?src=app";

            // Build URI with query string
            var builder = new UriBuilder(host_path);
            builder.Port = -1;
            var query = HttpUtility.ParseQueryString(builder.Query);
            query["src"] = "app";
            builder.Query = query.ToString();
            string url = builder.ToString();

            // Try making the request
            try{
                HttpResponseMessage response = await client.DeleteAsync(url);
                response.EnsureSuccessStatusCode();
                string responseBody = await response.Content.ReadAsStringAsync();
                output = responseBody;
            }
            catch(HttpRequestException e){
                string error = "\nException Caught! Message: " + e.Message;
                output = error;
            }

            // Return from Task
            return await Task.FromResult(output);
        }

        public class devInfo{
            public int account { get; set; }
            public int dev_id { get; set; }
            public string? last_update { get; set; }
            public string? net_ssid { get; set; }
            public string? net_pass { get; set; }
            //public IList<string>? data { get; set; }
            public IList<subDev>? data { get; set;}
        }

        public class subDev{
            public int dev_subid { get; set; }
            public int pow { get; set; }
            public int amp { get; set; }
            public string? dev_type { get; set; }
            public string? dev_name { get; set; }
        }

        static void Main(){
            // Test JSON Data
            //string test = "{\"account\":888999777,\"dev_id\":222,\"last_update\":\"2023-12-8-3600\",\"data\":[{\"dev_subid\":1,\"v_percent\":100,\"locked\":0}]}";

            // Test PUT - AWS Endpoint
            //Task<string> puttask1 = rest_put_aws("devState", test);
            //string putresp1 = puttask1.Result;
            //Console.WriteLine(putresp1);

            // Test GET - AWS Endpoint
            //Task<string> gettask1 = rest_get_aws("devState", "888999777", "222");
            //string getresp1 = gettask1.Result;
            //Console.WriteLine(getresp1);

            // Test DEL - AWS Endpoint
            //Task<string> deltask1 = rest_del_aws("888999777", "222", "0");
            //string delresp1 = deltask1.Result;
            //Console.WriteLine(delresp1);

            // Test GET - Device Endpoint
            Task<string> gettask2 = rest_get_dev("devInfo");
            string getresp2 = gettask2.Result;
            Console.WriteLine(getresp2);

            // TEST - Set Up devInfo for Device
            devInfo? json = JsonSerializer.Deserialize<devInfo>(getresp2);
            json.account = 888999777;
            json.dev_id = 222;
            json.last_update = "2024-5-10-" + ((int)(DateTime.Now.TimeOfDay.TotalMilliseconds / 1000)).ToString("");
            json.net_ssid = "";
            json.net_pass = "";
            string temp = JsonSerializer.Serialize(json);

            // Test PUT - Device Endpoint
            //Task<string> puttask2 = rest_put_dev("devInfo", "test data");
            Task<string> puttask2 = rest_put_dev("devInfo", temp);
            string putresp2 = puttask2.Result;
            Console.WriteLine(putresp2);

            // Test DEL - Device Endpoint
            //Task<string> deltask2 = rest_del_dev();
            //string delresp2 = deltask2.Result;
            //Console.WriteLine(delresp2);
        }
    }
}
