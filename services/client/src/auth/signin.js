import React, { useState, useEffect } from 'react';
import logo from '../assets/images/endless-logo.png';
import axios from "axios";
import man from '../assets/images/dashboard/user.png';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { withRouter } from "react-router";
import { BrowserRouter, Switch, Route,Redirect, useHistory } from 'react-router-dom';

import  {firebase_app, googleProvider, facebookProvider, twitterProvider, githubProvider,Jwt_token } from "../data/config";
import { handleResponse } from "../services/fack.backend";
import { useAuth0 } from '@auth0/auth0-react'
import { Login,LOGIN,YourName,Password,RememberMe,LoginWithAuth0,LoginWithJWT } from '../constant';

export default class Signin extends React.Component {
    constructor(props){
        super(props)
        this.state ={
            email: '',
            password: '',
        }
    }

    setEmail(e){
        this.setState({
            email: e
        })
    }

    setPassword(e){
        this.setState({
            password: e
        })
    }

    // componentWillMount(){
    //     localStorage.removeItem('token')
    //     localStorage.removeItem('authenticated')
    // }


    loginAuth(){
        var email = this.state.email
        var password = this.state.password
        const requestOptions = {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: ({ 'email':email, 'password':password })
        };
        
        return axios.post(`${process.env.PUBLIC_URL}/api/signin`, requestOptions)
        .then(user => {
            if (user.data.authenticated){
                localStorage.setItem('token', JSON.stringify(user.data));
                localStorage.setItem('role', user.data.role);
                localStorage.setItem("authenticated",true)
                window.location.replace('https://www.autoecom.org/dashboard/ecommerce')
                
            } else {
                alert(user.data.reason)
            }
        });
      }


    render(){
        return (
            <div>
                <div className="page-wrapper">
                    <div className="container-fluid p-0">
                        {/* <!-- login page start--> */}
                        <div className="authentication-main">
                            <div className="row">
                                <div className="col-md-12">
                                    <div className="auth-innerright">
                                        <div className="authentication-box">
                                            <div className="text-center">
                                                <img style={{width:'200px'}} src={logo} alt="" /></div>
                                            <div className="card mt-4">
                                                <div className="card-body">
                                                    <div className="text-center">
                                                        <h4 style={{opacity:'.7'}}>LOGIN</h4>
                                                        <h6 style={{opacity:'.2'}}>ENTER YOUR USERNAME OR PASSWORD</h6>
                                                    </div>
                                                    <form className="theme-form" >
                                                        <div className="form-group">
                                                            <label className="col-form-label pt-0" style={{fontSize:'10px', opacity:'.6'}}>EMAIL</label>
                                                            <input className="form-control" type="email" name="email"
                                                                value={this.state.email}
                                                                onChange={e => this.setEmail(e.target.value)}
                                                                placeholder='e.g. test@gmail.com'
                                                            />
                                                        
                                                        </div>
                                                        <div className="form-group">
                                                            <label className="col-form-label pt-0" style={{fontSize:'10px', opacity:'.6'}}>PASSWORD</label>
                                                            <input className="form-control" type="password" name="password"
                                                                value={this.state.password}
                                                                placeholder='e.g. *********'
                                                                onChange={e => this.setPassword(e.target.value)} />
                                                            
                                                        </div>
                                                        <div className="checkbox p-0">
                                                            <input id="checkbox1" type="checkbox" />
                                                            <label htmlFor="checkbox1">{RememberMe}</label>
                                                        </div>
                                                        <div className="form-group form-row mt-3 mb-0">
                                                            <button className="btn btn-primary btn-block" type="button" onClick={() => this.loginAuth()} >{Login}</button>
                                                        </div>
                                                        {/* <div className="form-group form-row mt-3 mb-0 button-auth">
                                                            <div className="col-md-6">
                                                                <button className="btn btn-secondary btn-block" type="button" onClick={() => loginWithJwt(email,password)} >{LoginWithJWT}</button>
                                                            </div>
                                                            <div className="col-md-6">
                                                                <button className="btn btn-success btn-block" type="button" onClick={loginWithRedirect} >{LoginWithAuth0}</button>
                                                            </div>
                                                        </div> */}
                                                        {/* <div className="login-divider"></div>
                                                        <div className="social mt-3">
                                                            <div className="form-group btn-showcase d-flex">
                                                                <button className="btn social-btn btn-fb d-inline-block" type="button" onClick={facebookAuth}> <i className="fa fa-facebook"></i></button>
                                                                <button className="btn social-btn btn-twitter d-inline-block" type="button" onClick={googleAuth}><i className="fa fa-google"></i></button>
                                                                <button className="btn social-btn btn-google d-inline-block" type="button" onClick={twitterAuth}><i className="fa fa-twitter"></i></button>
                                                                <button className="btn social-btn btn-github d-inline-block" type="button" onClick={githubAuth}><i className="fa fa-github"></i></button>
                                                            </div>
                                                        </div> */}
                                                    </form>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <ToastContainer />
                        {/* <!-- login page end--> */}
                    </div>
                </div>
            </div>
        )
    }

};