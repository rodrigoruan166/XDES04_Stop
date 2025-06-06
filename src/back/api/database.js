const mysql = require('mysql2');
require('dotenv').config();

const HOST = process.env.DATABASE_URL;
const PORT = process.env.PORT_DB;
const PASSWORD = process.env.PASSWORD_DB;
const USER = process.env.USER_DB;

const con = mysql.createConnection({
  host: HOST,
  user: USER,
  password: PASSWORD,
  port: PORT,
  database: "stop"
});

con.connect(function(err) {
  if (err) {
    throw err;
  }
  console.log("Connected!");
});

module.exports = {
    con
}