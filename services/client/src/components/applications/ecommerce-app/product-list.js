import React, { Fragment, useState} from 'react';
import Breadcrumb from '../../common/breadcrumb';
import DataTable from 'react-data-table-component';
import axios from 'axios';
import { Truck, ShoppingCart, Trash } from 'react-feather';
import { Button, Modal, ModalHeader, ModalBody, ModalFooter } from 'reactstrap';



export default class ProductList extends React.Component {
    constructor(props){
        super(props)
        this.state = {
            orders:[],
            shipping: false,
            shippingLoading: false,
            selectedOrder: '',
            shippingInfo: null,
            currentStore: null,
            orderSubmission: false,
            actualCost: null,
            orderNumber: null,
            stores: null,
        }
    }

    componentDidMount(){
        axios.get('http://ecommerce-aio.herokuapp.com/allOrders')
        .then((result)=>{
            this.setState({
                orders: result.data,
                currentStore: localStorage.getItem('token')
            })
        })

        axios.get('http://ecommerce-aio.herokuapp.com/allStores')
        .then((result)=>{
            this.setState({
                stores: result.data
            })
        })
    }

    cancelOrder(e, order){
        var answer = window.confirm("Are you sure you want to cancel this order? (Order Cancellation Rate should not be higher than 5%)")

        if (answer) {
            axios.get('http://ecommerce-aio.herokuapp.com/cancel?id=' + order['id'] + '&storeId=' + localStorage.getItem('id'))
            .then((result)=>{
                this.setState({
                    orders: result.data,
                    currentStore: localStorage.getItem('id')
                })
            })
        }
    }

    closeShipping(){
        this.setState({
            shippingInfo: null,
            shipping: false,
        })
    }

    setActualCost(e){
        this.setState({
            actualCost: e.target.value
        })
    }

    setOrderNumber(e){
        this.setState({
            orderNumber: e.target.value
        })
    }

    closeOrder(){
        this.setState({
            orderSubmission: false,
        })
    }

    submitOrder(){
        if (!this.state.orderNumber && !this.state.actualCost){
            alert('Order # and Cost is Missing.')
        } else if (!this.state.orderNumber){
            alert('Order # is Missing.')
        } else if (!this.state.actualCost){
            alert('Total Cost is Missing.')
        } else {
            var orderDetails = {
                order: this.state.selectedOrder,
                storeId: JSON.parse(localStorage.getItem('token'))['user_id'],
                purchaseOrder: this.state.orderNumber,
                actualCost: this.state.actualCost,
                profit: Math.round(((parseFloat(this.state.selectedOrder['purchase_price'])*.85)-this.state.actualCost)*10)/10,
                roi: Math.round(((Math.round(((parseFloat(this.state.selectedOrder['purchase_price'])*.85)-this.state.actualCost)*10)/10)/this.state.actualCost)*100) 
            }

            axios.post('http://localhost:4000/markOrdered', orderDetails)
            .then((result)=>{
                if (result.status == 200){
                    this.closeOrder()
                } else {
                    alert('Error. Please try again.')
                }
            })

        }
    }

    openInNewTab(e, order) {

        this.setState({
            orderSubmission: true,
            selectedOrder: order
        })

        window.open("https://www.amazon.com/gp/offer-listing/" + order['supplier_url'].split('/dp/')[1], '_blank').focus();
    }

    generateShipping(){
        this.setState({
            shippingLoading: true
        })

        axios.post('http://localhost:4000/getTracking', this.state.selectedOrder)
        .then((result)=>{
            this.setState({
                shippingInfo: result.data
            })
        })
    }


    toggleShipping(e, order){
        this.setState({
            shipping: !this.state.shipping,
            selectedOrder: order
        })
    }

    render(){
        const columns = [
            {
                name: 'Name',
                selector: row => row['name'],
                sortable: true,
            },
            {
                name: 'URL',
                selector: row => row['url'],
                sortable: true,
            },
        ];

        return (
            <Fragment>
                <Breadcrumb title="Orders" parent="Ecommerce" />
                <div className="container-fluid">
                    <div className="row">
                    <Modal isOpen={this.state.shipping}>
                            {/* <ModalHeader toggle={this.state.shipping}>ModalTitle</ModalHeader> */}
                            <ModalBody>
                                {this.state.selectedOrder != '' ? <div>
                                    <p>Generate a Shipping Number for</p>
                                    <input style={{color:'black'}} value={this.state.selectedOrder['raw_json']['shippingInfo']['postalAddress']['city']}></input>
                                    <p>Arriving Before:</p>
                                    <input style={{color:'black'}} value={new Date(this.state.selectedOrder['raw_json']['shippingInfo']['estimatedShipDate']).toLocaleDateString("en-US")}></input>
                                    <p>For Order # {this.state.selectedOrder['id']}</p>
                                    <p>{this.state.selectedOrder['raw_json']['shippingInfo']['postalAddress']['name']}</p>

                                    {this.state.shippingInfo ? <div>
                                    <p>Shipping Number Generated</p>
                                    <p>Origin City: {this.state.shippingInfo['originCity']}</p>
                                    <p>Origin State: {this.state.shippingInfo['originState']}</p>
                                    <p>Shipped on: {new Date(this.state.shippingInfo['shippedAt']).toLocaleDateString("en-US")}</p>
                                    <p>{this.state.shippingInfo['trackingNr']}</p>
                                    </div> : null}
                                </div>
                                : null}
                                
                            </ModalBody>
                            <ModalFooter>
                                <Button color="primary" onClick={()=>{this.closeShipping()}}>Exit</Button>{' '}
                                <Button color="primary" onClick={()=>{this.generateShipping()}}>Get Tracking</Button>{' '}
                                {/* <Button color="secondary" onClick={toggle1}>{Cancel}</Button> */}
                            </ModalFooter>
                        </Modal>

                        <Modal isOpen={this.state.orderSubmission}>
                            {/* <ModalHeader toggle={this.state.shipping}>ModalTitle</ModalHeader> */}
                            <ModalBody style={{width:'100%'}}>
                                {this.state.selectedOrder != '' ? <div style={{display:'flex', flexDirection:'row', width:'100%', justifyContent:'space-between'}}>
                                    <div style={{width:'50%'}}>
                                        <p style={{fontWeight:600}}>Order # {this.state.selectedOrder['id']}</p>
                                        { Object.entries(this.state.selectedOrder['raw_json']['shippingInfo']['postalAddress']).map((data)=>{
                                            {return <tr>{data[1]}</tr>}
                                        })}

                                        <div style={{marginTop:'20px'}}>
                                            <tr>Net Earnings: {Math.round(parseFloat(this.state.selectedOrder['purchase_price'])*.85*10)/10}</tr>
                                            <tr>Est. Cost: {this.state.selectedOrder['supplier_price']}</tr>
                                            <tr>Est. Profit: {Math.round(((parseFloat(this.state.selectedOrder['purchase_price'])*.85) - (parseFloat(this.state.selectedOrder['supplier_price'])*(parseFloat(this.state.selectedOrder['raw_json']['orderLines']['orderLine'].length))))*10)/10}</tr>
                                            <tr>Est Margin: {Math.round(Math.round(((parseFloat(this.state.selectedOrder['purchase_price'])*.85) - (parseFloat(this.state.selectedOrder['supplier_price'])*(parseFloat(this.state.selectedOrder['raw_json']['orderLines']['orderLine'].length))))*10)/10 / (parseFloat(this.state.selectedOrder['supplier_price'])*(parseFloat(this.state.selectedOrder['raw_json']['orderLines']['orderLine'].length)))*100)}%</tr>
                                        </div>
                                                                          </div>
                                    <div style={{display:'flex', flexDirection:'column'}}>
                                        <label>Enter the actual Order Cost</label>
                                        <input style={{color:'black'}} value={this.state.actualCost} onChange={(e) => {this.setActualCost(e)}}></input>
                                        <label>Purchase Order Number: </label>
                                        <input style={{color:'black'}} value={this.state.orderNumber} onChange={(e) => {this.setOrderNumber(e)}}></input>
                                        {/* <input style={{color:'black'}} value={new Date(this.state.selectedOrder['raw_json']['shippingInfo']['estimatedShipDate']).toLocaleDateString("en-US")}></input> */}
                                        
                                        
                                        <div style={{marginTop:'20px'}}>
                                            {this.state.actualCost != null ? <tr>Actual Cost: {this.state.actualCost}</tr> : null}
                                            {this.state.actualCost != null ? <tr>Actual Profit: {Math.round(((parseFloat(this.state.selectedOrder['purchase_price'])*.85)-this.state.actualCost)*10)/10}</tr> : null}
                                            {this.state.actualCost != null ? <tr>Actual ROI: {Math.round(((Math.round(((parseFloat(this.state.selectedOrder['purchase_price'])*.85)-this.state.actualCost)*10)/10)/this.state.actualCost)*100)}%</tr> : null}
                                        </div>
                                    </div>
                                </div> : null}
                                
                            </ModalBody>
                            <ModalFooter>
                                <Button color="primary" onClick={()=>{this.closeOrder()}}>Exit</Button>{' '}
                                <Button color="primary" onClick={()=>{this.submitOrder()}}>Mark as Ordered</Button>{' '}
                                {/* <Button color="secondary" onClick={toggle1}>{Cancel}</Button> */}
                            </ModalFooter>
                        </Modal>
                        {/* <!-- Individual column searching (text inputs) Starts--> */}
                        <div className="col-sm-12">
                            <div className="card">
                                <div className="card-header">
                                    <h5>{"Individual column searching (text inputs)"} </h5><span>{"The searching functionality provided by DataTables is useful for quickly search through the information in the table - however the search is global, and you may wish to present controls that search on specific columns."}</span>
                                </div>
                                <div className="card-body">
                                    <div className="table-responsive product-table">
                                        <table className="table table-bordernone" >
                                            <thead>
                                            <tr>
                                                <th scope="col">#</th>
                                                <th scope="col">Item</th>
                                                <th scope="col">Price</th>
                                                <th scope="col">Rev.</th>
                                                <th scope="col">Ord. #</th>
                                                <th scope="col">Est. Cost</th>
                                                <th scope="col">Cost</th>
                                                <th scope="col">Net</th>
                                                <th scope="col">ROI</th>
                                                <th scope="col">Action</th>
                                                <th scope="col">Status</th>

                                            </tr>
                                            </thead>
                                            <tbody>
                                                {this.state.orders.map((order)=>{
                                                    if (order['status'].toUpperCase() != 'DELIVERED' && order['status'].toUpperCase() != 'SHIPPED' && order['status'].toUpperCase() != 'CANCELLED'){
                                                        return <tr>
                                                            <td>{order['id']} <span style={{fontSize:'10px'}}>{this.state.stores != null ? this.state.stores[order.store_id] : null }</span></td>
                                                            <td>{order['raw_json']['shippingInfo']['postalAddress']['name'].toUpperCase()}</td>
                                                            <td>{order['purchase_price']}</td>
                                                            <td>{Math.round(parseFloat(order['purchase_price'])*.85*10)/10}</td>
                                                            <td>{order['supplier_order_id']}</td>
                                                            <td>{order['supplier_price']}</td>
                                                            <td><input type='text'></input></td>
                                                            <td>{Math.round(((parseFloat(order['purchase_price'])*.85) - (parseFloat(order['supplier_price'])*(parseFloat(order['raw_json']['orderLines']['orderLine'].length))))*10)/10}</td>
                                                            <td>{Math.round(Math.round(((parseFloat(order['purchase_price'])*.85) - (parseFloat(order['supplier_price'])*(parseFloat(order['raw_json']['orderLines']['orderLine'].length))))*10)/10 / (parseFloat(order['supplier_price'])*(parseFloat(order['raw_json']['orderLines']['orderLine'].length)))*100)}%</td>
                                                            <td>{order['status'].toUpperCase()}</td>
                                                            <td style={{width:'100%'}}><Truck size={16} onClick={(e)=>{this.toggleShipping(e, order)}} style={{margin:'5px'}}/><ShoppingCart size={16} onClick={(e)=>{this.openInNewTab(e, order)}} style={{margin:'5px'}}/><Trash onClick={(e)=>{this.cancelOrder(e, order)}} size={16} style={{margin:'5px'}}/></td>
                                                        </tr>
                                                    }
                                                })}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                    </div>
                </div>
            </Fragment>
    )}
};