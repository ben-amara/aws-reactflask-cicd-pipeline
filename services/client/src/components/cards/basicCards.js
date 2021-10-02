import React, { Fragment } from 'react';
import axios from 'axios';
import Breadcrumb from '../common/breadcrumb';
import {BasicCard,FlatCard,WithoutShadowCard,IconInHeading,CardSubTitle,CardWithFooter,Card_Footer,SuccessColorCard,PrimaryColorCard,SecondaryColorCard,PrimaryColorBody,PrimaryColorHeader,PrimaryColorFooter} from "../../constant";
import Axios from 'axios';

export default class BasicCards extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            supplierURL: '',
            asin: '',
            walmart: '',
            sku: '',
            initial_price: '',
            handling: 3,
            buybox: '',
            selling_fee: '',
            cost: '',
            profit:  '',
            margin: '',
            walmart_image: '',
            amz_image: '',
            loading: false,
        }

        // this.searchASIN = this.searchASIN.bind(this)
    }

    updateSupplierURL(url){

        let asin = ''

        try {
            if (url.target.value.split('/dp/')[1].split('/')[0]){

                asin = url.target.value.split('/dp/')[1].split('/')[0]
                if (asin.split('?')){
                    asin = asin.split('?')[0]
                }
            }

            this.setState({
                supplierURL: url.target.value,
                asin: asin
            })

            if (asin != ''){
                this.setState({
                    loading:true
                })

                axios("https://ecommerce-aio.herokuapp.com/searchASIN?ASIN=" + asin)
                .then((result)=>{
                    if (result.data.status == 'profitable'){
                        this.setState({
                            loading:false,
                            walmart: result.data.walmart,
                            sku: result.data.sku,
                            initial_price: result.data.initial_price,
                            handling: 3,
                            buybox: result.data.buybox,
                            selling_fee: result.data.selling_fee,
                            cost: result.data.cost,
                            profit:  result.data.profit,
                            margin: result.data.margin,
                            walmart_image: result.data.walmart_image,
                            amz_image: result.data.amz_image
                        })
                    } else {
                        this.setState({
                            loading: false
                        })
                    }
                    
                })
            }

        } catch {
            console.log('Error')
        }
    }

    // searchASIN(){
    //     debugger
    //     fetch("https://ecommerce-aio.herokuapp.com?ASIN=" + this.state.asin)
    //     .then((result)=>{
    //         debugger
    //     })
    // }

    render(){
        return (
            <Fragment>
                <Breadcrumb title="Create Listing" parent="Card" />
                <div className="container-fluid">
                    <div className="row">
                        <div className="col-sm-12 col-xl-6">
                            <div className="card">
                                <div className="col-md-4 mb-3" style={{marginTop:'20px', dispaly:'flex', flexDirection:'row', alignItems:'center'}}>
                                    <div>
                                        <label htmlFor="validationCustom01" style={{letterSpacing:'1px', fontWeight:'600', fontSize:'10px'}}>SUPPLIER URL</label>
                                        <input className="form-control" name="firstName" type="text" onChange={(event)=>{this.updateSupplierURL(event)}} placeholder="Supplier Listing URL" />
                                        <span style={{fontSize:'10px', opacity:'.5', marginTop:'20px'}}>URL of an existing listing on Supplier Website.</span>
                                        <div className="valid-feedback"></div>
                                    </div>

                                    {this.state.loading ? <div className="loader-box">
                                        <div className="loader">
                                        <div className="line bg-info"></div>
                                        <div className="line bg-info"></div>
                                        <div className="line bg-info"></div>
                                        <div className="line bg-info"></div>
                                        </div>
                                    </div> : ''}
                                </div>

                                {this.state.walmart != '' ? <div>

                                    
                                    
                                    <div className="card-header">
                                        <h5>Walmart Listing</h5>
                                    </div>
                                    
                                    <div className="col-md-4 mb-3" style={{marginTop:'20px', maxWidth:'85%'}}>
                                        <label htmlFor="validationCustom01" style={{letterSpacing:'1px', fontWeight:'600', fontSize:'10px'}}>WALMART URL</label>
                                        <input className="form-control" name="firstName" type="text" placeholder="Walmart Listing URL" value={this.state.walmart}/>
                                        <span style={{fontSize:'10px', opacity:'.5', marginTop:'20px'}}>URL of an existing listing on Walmart.</span>
                                        <div className="valid-feedback"></div>
                                    </div>

                                    <div className="col-md-4 mb-3" style={{marginTop:'20px', maxWidth:'85%'}}>
                                        <label htmlFor="validationCustom01" style={{letterSpacing:'1px', fontWeight:'600', fontSize:'10px', opacity:'.5'}}>LISTING SKU</label>
                                        <input className="form-control" name="firstName" type="text" placeholder="Walmart Listing URL" value={this.state.sku}/>
                                        <span style={{fontSize:'10px', opacity:'.5', marginTop:'20px'}}>Your custom unique identifier for this listing (default: UPC code 681131174282-AE)</span>
                                        <div className="valid-feedback"></div>
                                    </div>

                                    <div className="col-md-4 mb-3" style={{marginTop:'20px', maxWidth:'85%'}}>
                                        <label htmlFor="validationCustom01" style={{letterSpacing:'1px', fontWeight:'600', fontSize:'10px', opacity:'.5'}}>INITIAL PRICE</label>
                                        <input className="form-control" name="firstName" type="text" placeholder="Walmart Listing URL" value={this.state.initial_price}/>
                                        <span style={{fontSize:'10px', opacity:'.5', marginTop:'20px'}}>Initial Price for listing</span>
                                        <div className="valid-feedback"></div>
                                    </div>

                                    <div className="col-md-4 mb-3" style={{marginTop:'20px', maxWidth:'85%'}}>
                                        <label htmlFor="validationCustom01" style={{letterSpacing:'1px', fontWeight:'600', fontSize:'10px', opacity:'.5'}}>HANDLING TIME (DAYS)</label>
                                        <input className="form-control" name="firstName" type="text" placeholder="Walmart Listing URL" value={this.state.handling}/>
                                        <span style={{fontSize:'10px', opacity:'.5', marginTop:'20px'}}>Handling Days for item (max. days before it's shipped)</span>
                                        <div className="valid-feedback"></div>
                                    </div>

                                    <div className="col-md-4 mb-3" style={{marginTop:'20px', display:'flex', flexDirection:'row', width:'400px', maxWidth:'85%'}}>
                                        
                                            {(this.state.walmart_image != '' && this.state.amz_image != '') ? <div style={{display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center'}}>
                                                <img style={{width:'100px', height:'100px', margin:'0 10px 10px 10px', padding:'0 10px 10px 10px'}} src={this.state.walmart_image}></img>
                                                <img style={{width:'100px', height:'100px', margin:'10px 10px 10px 10px', padding:'10px'}} src={this.state.amz_image}></img>
                                            </div> : ''}

                                        <div style={{marginLeft:'30px'}}>
                                            <p style={{fontSize:'10px', margin:'0', fontWeight:'600', marginBottom:'10px'}}>PRODUCT TITLE</p>
                                            <p style={{fontSize:'10px', margin:'0'}}>Buybox price: ${this.state.buybox}</p>
                                            <p style={{fontSize:'10px', margin:'0'}}>Initial price: ${this.state.initial_price}</p>
                                            <p style={{fontSize:'10px', margin:'0'}}>Estimated selling fee: ${this.state.selling_fee}</p>
                                            <p style={{fontSize:'10px', margin:'0'}}>Total cost: ${this.state.cost}</p>
                                            <p style={{fontSize:'10px', margin:'0'}}>Estimated profit: ${this.state.profit}</p>
                                            <p style={{fontSize:'10px', margin:'0'}}>Profit margin: {this.state.margin}%</p>
                                            {this.state.supplierURL != '' ? <p style={{fontSize:'10px', margin:'0'}}>ASIN: {this.state.asin}</p> : ''}

                                        </div>
                                    </div>
                                    
                                    </div> : ''}

                                
                            </div>
                        </div>
                    </div>
                </div>
            </Fragment>
        )
    }
    
}