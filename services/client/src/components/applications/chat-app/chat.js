import Axios from 'axios';
import React, { useEffect, useState } from 'react';
import Breadcrumb from '../../common/breadcrumb';

var images = require.context('../../../assets/images', true);


export default class Chat extends React.Component {
    constructor(props){
        super(props)
        this.state = {
            conversations: [],
            messageBody: '',
            currentMessage: '',
            selectedConvo: ''
        }    
    }

    componentDidMount(){
        Axios.get('http://ecommerce-aio.herokuapp.com/viewConversations')
        .then((result)=>{
            this.setState({
                conversations: result.data,
                currentMessage: '',
                selectedConvo: result.data[0].sid
            })
        })
    }

    updateSelectedConvo(event, convo){
        this.setState({
            selectedConvo: convo.sid
        })
    }

    sendMessage(event, convo){
        this.setState({
            currentMessage: '',
        })

        let conversations = this.state.conversations

        Axios.get('http://ecommerce-aio.herokuapp.com/sendMessage?sid=' + this.state.selectedConvo + '&body=' + this.state.messageBody)
        .then(()=>{
            Axios.get('http://ecommerce-aio.herokuapp.com/viewConversations')
            .then((result)=>{
                this.setState({
                    conversations: result.data,
                    currentMessage: '',
                    selectedConvo: this.state.selectedConvo,
                    messageBody: ''
                })
            })
        })
        
        
    }

    handleMessageChange(event){
        this.setState({
            messageBody: event.target.value
        })
    }

    
    render(){
        return (<div>
                    <Breadcrumb title="Chat App" parent="Apps" />
                    <div className="container-fluid">
                        <div className="row">
                            <div className="col call-chat-sidebar col-sm-12">
                                <div className="card">
                                    <div className="card-body chat-body">
                                        <div className="chat-box">
                                            <div className="chat-left-aside">
                                                
                                                {this.state.conversations.map((convo)=>{
                                                    return <div style={{marginBottom:'10px', paddingBottom:'10px', backgroundColor:'#ffffff'}} onClick={(e) => this.updateSelectedConvo(e, convo)}>
                                                        <p>{convo.name}</p>
                                                        {/* <p style={{padding:'0', margin:'0', opacity:'.25'}}>{convo.messages[0].body}</p> */}
                                                    </div>
                                                })}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="col call-chat-body">
                                <div className="card">
                                    <div className="card-body p-0">
                                        <div className="row chat-box">
                                            <div className="col pr-0 chat-right-aside">
                                                <div className="chat">
                                                    <div className="chat-header clearfix">
                                                        <div className="about">
                                                            <div className="name">
                                                                {/* {selectedUser.name} */}
                                                            </div>
                                                            <div className="status digits" >
                                                            </div>
                                                        </div>
                                                        <ul className="list-inline float-left float-sm-right chat-menu-icons">
                                                            <li className="list-inline-item"><a href="#javascript"><i className="icon-search"></i></a></li>
                                                            <li className="list-inline-item"><a href="#javascript"><i className="icon-clip"></i></a></li>
                                                            <li className="list-inline-item"><a href="#javascript"><i className="icon-headphone-alt"></i></a></li>
                                                            <li className="list-inline-item"><a href="#javascript"><i className="icon-video-camera"></i></a></li>
                                                        </ul>
                                                    </div>

                                                    <div className="chat-history chat-msg-box custom-scrollbar" style={{display:'flex', flexDirection:'column', width:'100%', height:'500px', marginBottom:'100px', overflowY: 'scroll'}}>
                                                        {this.state.conversations.map((convo)=>{
                                                            debugger
                                                            if (convo.sid == this.state.selectedConvo){
                                                                return convo.messages.map((message)=>{

                                                                    if (message.sender == 'AutoEcom'){
                                                                        return <div style={{marginLeft: 'auto', textAlign:'right'}}>
                                                                        <p style={{backgroundColor:'#4466f2', color:'white', padding:'5px 10px 5px 10px', borderRadius:'10px', margin:'10px'}}>{message.body}</p>
                                                                        <p style={{opacity:'.4', padding:'5px 10px 5px 10px', borderRadius:'10px', margin:'10px'}}>{message.sender}</p>
                                                                    
                                                                    </div>
                                                                    } else {
                                                                        return <div style={{marginRight: 'auto', textAlign:'left'}}>
                                                                        <p style={{backgroundColor:'#EDEDED', color:'#444444', padding:'5px 10px 5px 10px', borderRadius:'10px', margin:'10px'}}>{message.body}</p>
                                                                        <p style={{opacity:'.4', padding:'5px 10px 5px 10px', borderRadius:'10px', margin:'10px'}}>{message.sender}</p>
                                                                    
                                                                        
                                                                    </div>
                                                                    }
                                                                    
                                                                })
                                                            }
                                                            
                                                        })}

                                                    </div>
                                                    <div className="chat-message clearfix">
                                                        <div className="row">
                                                            
                                                            <div className="col-xl-12 d-flex">
                                
                                                                <div className="input-group text-box">
                                                                    <input
                                                                        type="text"
                                                                        className="form-control input-txt-bx"
                                                                        placeholder="Type a message......"
                                                                        value={this.state.messageBody}
                                                                        onChange={(e) => this.handleMessageChange(e)}
                                                                    />
                                                                    <div className="input-group-append">
                                                                        <button className="btn btn-primary" type="button" onClick={() => this.sendMessage('send')} >Send</button>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                            
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
        )
    }
}
