pragma solidity 0.8.0;


contract app {

    struct video{
        string hash;
        string name;
        string date_added;
        string url;


    }
    struct user{

        string username;
        string email;
        uint num;


        string date_end;

        string private_address;
        string secret_api;
        string public_api;
        
        uint num_liked;
        string[] public liked;
    }
    
    uint num_ad = 0;
    address public owner;

    string[] public all_hashes;
    address[] public addresses;
    
    mapping(email => address) public emails;

    mapping(address => video[]) public videos;
    mapping(address => user) public users;
    mapping(uint => address) public ad;

    mapping(string => uint) public likes;

    constructor(){
        owner = msg.sender;
    }

    modifier onlyOwner {
        require(msg.sender == owner);
        _;
    }

   function add_user(string memory _username, string memory _email,string memory private_address,string memory secret_api,string memory public_api) public {
       uint num = 0;
       
       uint _num_liked = 0;
       string[] public _liked;
       emails[_email] = msg.sender;
     
       users[msg.sender] = user(_username,_email,num,"",private_address,secret_api,public_api,_num_liked,_liked);
       ad[num_ad++] = msg.sender;
       
   }   
   
   function change_api(string memory _secret_api,string memory _public_api) public{
       users[msg.sender].secret_api = _secret_api;
       users[msg.sender].public_api = _public_api;
    }

    function check_api(string memory _secret_api,string memory _public_api) public view returns (bool){
       bytes memory b1 = bytes(users[msg.sender].secret_api);
       bytes memory b2 = bytes(_secret_api);
       bytes memory p1 = bytes(users[msg.sender].public_api);
       bytes memory p2 = bytes(_public_api);

       uint256 l1 = b1.length;
       if (l1 != b2.length || p2.length != p1.length ) return false;
       for (uint256 i=0; i<l1; i++) {
           if (b1[i] != b2[i]) return false;
       }
       for(uint256 i=0; i<p1.length;i++){
           if(p1[i] != p2[i]) return false;
       }
       return true;
    }

   function login(string memory _username) public view returns(bool){
       string memory username_check = users[msg.sender].username;

       bytes memory b1 = bytes(_username);
       bytes memory b2 = bytes(username_check);

       uint256 l1 = b1.length;
       if (l1 != b2.length || p2.length != p1.length ) return false;
       for (uint256 i=0; i<l1; i++) {
           if (b1[i] != b2[i]) return false;
       }
       return true;
   }     
   
   function add_video(string memory _hash,string memory _date,string memory _name,string memory _url) public {
       videos[msg.sender].push(video(_hash,_name,_date,_url));
       users[msg.sender].num++;
       likes[_hash] = 0;

       all_hashes.push(_hash);

   }

   function delete_video(uint  _num) public {
       delete(videos[msg.sender][_num]);
       users[msg.sender].num--;
   }
   
   function num_videos() public  view returns(uint){

       return users[msg.sender].num;
   }

   function getvideo(uint  _num1) public view returns(string[] memory){
       string[] memory list = new string[](4);

       list[0] = videos[msg.sender][_num1].hash;
       list[1] = videos[msg.sender][_num1].name;
       list[2] = videos[msg.sender][_num1].date_added;
       list[3] = videos[msg.sender][_num1].url;

       return list;

   }

   function add_like(string memory _hash) public {
       likes[_hash]++;
       users[msg.sender].liked.push(_hash);
   }
   
   function remove_like(string _hash) public{

       for (uint i=0; i<user[msg.sender].num_liked; i++) {
           if (users[msg.sender].liked[i] == _hash){
               users[msg.sender].liked.remove(_hash);
               users[msg.sender].num_liked--;
               likes[_hash]--;
           }
       }

   }

   function get_allvideos() public view returns(string[] memory,string[] memory,uint[] memory){
       uint[] all_likes;
       for(uint i=0;i<all_hashes.length;i++){
           all_likes.push(likes[all_hashes[i]);
       }
       return all_hashes,users[msg.sender].liked,all_likes;
   }

}
