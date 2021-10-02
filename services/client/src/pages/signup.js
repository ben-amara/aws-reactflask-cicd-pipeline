import React, { Fragment } from 'react';
import logo from '../assets/images/endless-logo.png';
import axios from "axios";
import { FirstName, LastName, Username,Login,Password,SignUp,BOD } from '../constant';

export default class Signup extends React.Component{
    constructor(props){
        super(props)
        this.state = {
            email: '',
            password: '',
            name: ''
        }
    }

    updateName(e){
        this.setState({
            name: e.target.value
        })
    }

    updateEmail(e){
        this.setState({
            email: e.target.value
        })
    }

    updatePassword(e){
        this.setState({
            password: e.target.value
        })
    }

    submitDeal(e){
        e.preventDefault()

        var name = this.state.name
        var email = this.state.email
        var password = this.state.password

        const requestOptions = {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: ({ 'name':name, 'email':email, 'password':password })
        };
        
        return axios.post('https://www.autoecom.org/api/signup', requestOptions)
        .then(user => {
            if (user.data.authenticated){
                localStorage.setItem('token', user.data);
                window.location.href = `https://www.autoecom.org/`
                return user;
            } else {
                alert(user.data.reason)
            }
        });
    }



    render(){
        return (
            <Fragment>
                <div className="page-wrapper">
                    <div className="container-fluid">
                        {/* <!-- sign up page start--> */}
                        <div className="authentication-main">
                            <div className="row">
                                <div className="col-sm-12 p-0">
                                    <div className="auth-innerright">
                                        <div className="authentication-box">
                                            <div className="text-center"><img style={{width:'200px'}} src={logo} alt="" /></div>
                                            <div className="card mt-4 p-4">
                                                <h4 className="text-center">{"NEW USER"}</h4>
                                                <h6 className="text-center">{"Enter your Username and Password For Signup"}</h6>
                                                <form className="theme-form">
                                                    <div className="form-row">
                                                        <div className="col-md-6">
                                                            <div className="form-group">
                                                                <label className="col-form-label">Name</label>
                                                                <input className="form-control" onChange={(e)=>{this.updateName(e)}} type="text" placeholder="John" />
                                                            </div>
                                                        </div>
                                                        {/* <div className="col-md-6">
                                                            <div className="form-group">
                                                                <label className="col-form-label">{LastName}</label>
                                                                <input className="form-control" type="text" placeholder="Deo" />
                                                            </div>
                                                        </div> */}
                                                    </div>
                                                    <div className="form-group">
                                                        <label className="col-form-label">Email</label>
                                                        <input className="form-control" onChange={(e)=>{this.updateEmail(e)}} type="text" placeholder="test@test.com" />
                                                    </div>
                                                    <div className="form-group">
                                                        <label className="col-form-label">{Password}</label>
                                                        <input className="form-control" onChange={(e)=>{this.updatePassword(e)}} type="password" placeholder="**********" />
                                                    </div>
                                                    <div className="form-row">
                                                        <div className="col-sm-4">
                                                            <button className="btn btn-primary" onClick={(e)=>{this.submitDeal(e)}} type="submit">Sign Up</button>
                                                        </div>
                                                        <div className="col-sm-8">
                                                            <div className="text-left mt-2 m-l-20">{"Are you already user?"}  <a className="btn-link text-capitalize" href="login.html">{Login}</a></div>
                                                        </div>
                                                    </div>
                                                </form>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        {/* <!-- sign up page ends--> */}
                    </div>
                </div>
            </Fragment>
        );
    }
}