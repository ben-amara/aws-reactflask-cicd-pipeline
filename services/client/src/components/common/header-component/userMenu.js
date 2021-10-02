import React, { Fragment, useState, useEffect } from 'react';
import man from '../../../assets/images/dashboard/user.png';
import { User, Mail, Lock, Settings, LogOut } from 'react-feather';
import {firebase_app} from "../../../data/config";
import { Link } from 'react-router-dom';
import { withRouter } from 'react-router';
import {useAuth0} from '@auth0/auth0-react'
import {EditProfile,Inbox,LockScreen} from '../../../constant'

const UserMenu = ({ history }) => {

    const [profile, setProfile] = useState('');
    // auth0 profile

    const authenticated = JSON.parse(localStorage.getItem("authenticated"))
    const auth0_profile = JSON.parse(localStorage.getItem("auth0_profile"))

    useEffect(() => {
        setProfile(localStorage.getItem('profileURL') || man);
    }, []);

    const Logout = () => {
        localStorage.removeItem('authenticated')
        localStorage.removeItem('token')
        history.push(`${process.env.PUBLIC_URL}/login`)
    }

    const CheckForToken =()=>{
        var name = localStorage.getItem('token').name
        return name
    }


    return (
        <Fragment>
            <li className="onhover-dropdown">
                <div className="media align-items-center">
                    <div>
                        {localStorage.getItem('token') ? CheckForToken : null}
                    </div>
                </div>
                <ul className="profile-dropdown onhover-show-div p-20 profile-dropdown-hover">
                    {/* <li><Link to={`${process.env.PUBLIC_URL}/users/userEdit`}><User />{EditProfile}</Link></li>
                    <li><Link to={`${process.env.PUBLIC_URL}/email-app/emailDefault`}><Mail />{Inbox}</Link></li>
                    <li><a href="#javascript"><Lock />{LockScreen}</a></li>
                    <li><a href="#javascript"><Settings />{"Settings"}</a></li> */}
                    <li><a onClick={authenticated ? Logout : Logout} href="#javascript" ><LogOut /> {"Log out"}</a></li>
                </ul>
            </li>
        </Fragment>
    );
};


export default withRouter(UserMenu);