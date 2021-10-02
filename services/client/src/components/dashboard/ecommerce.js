import React ,{Fragment ,useEffect} from 'react';
import Breadcrumb from '../common/breadcrumb';
import { DollarSign, MapPin, X, TrendingDown, ArrowUp, ShoppingCart } from 'react-feather';
import Slider from 'react-slick';
import six from  "../../assets/images/user/6.jpg";
import two from "../../assets/images/user/2.png";
import three from "../../assets/images/user/3.jpg";
import four from "../../assets/images/user/4.jpg";
import five from "../../assets/images/user/5.jpg";
import fifteen from "../../assets/images/user/15.png"
import { saleData , saleOptions,incomeData , incomeOptions,profitData,profitOptions, staticData ,staticOptions} from '../../data/default';
import { Line } from 'react-chartjs-2';
import CountUp from 'react-countup';
import {TotalEarning,TotalWebVisitor,TotalSaleProduct,CompanyLoss,Name,Sale,Stock,Categories,AlanaSlacker,PaymentDone,WorkProcess,SaleCompleted,TotalSale,BestSellers,PaymentStatus,BasicInformation,Portfolio,LegalDocument,Interest,ProductInfo,BillingDetails,Logs,Computer,Active,Headphone,Disable,Furniture,Paused,Shoes,OnWay,Review,TotalIncome,ProfileStatus,TotalProfit,ShoppingCarts} from '../../constant'
import axios from 'axios';
var Knob = require('knob')// browserify require
var primary = localStorage.getItem('primary_color') || '#4466f2';

export default class Ecommerce extends React.Component {
  constructor(props){
    super(props)
    this.state = {
      totalGross: 0,
      totalItems: 0,
      todaysOrders: 0,
      todaysProfit: 0,
      selectedStore:null,
      bestSellers: [],
      storeStatus: [],
      graphData: [],
      recent: [],
      lateOrders: [],
      runningStores: 0,
      orders: 0,
      profit: 0,
      revenue: 0,
      roi: 0,
      spent: 0,
      avg_profit: 0,
      settings: {
        dots: false,
        infinite: true,
        speed: 500,
        slidesToShow: 4,
        slidesToScroll:1,
        arrows: false,
        autoplay:true,
        responsive: [
          {
            breakpoint: 1024,
            settings: {
              slidesToShow: 3,
            }
          },
          {
            breakpoint: 600,
            settings: {
              slidesToShow: 3,
            }
          },
          {
            breakpoint: 480,
            settings: {
              slidesToShow: 2,
            }
          },
          {
            breakpoint: 370,
            settings: {
              slidesToShow: 1,
            }
          }
        ]
      }
    }
  }

  useEffect(){
    var profit = Knob({
      value: 35,
      left: 1,
      angleOffset: 90,
      className: "review",
      thickness: 0.1,
      width: 285,
      height: 285,
      fgColor: primary,
      bgColor: '#f6f7fb',
      lineCap: 'round'
  })
    document.getElementById('profit').appendChild(profit) 
  }

  componentDidMount(){
    var user = localStorage.getItem('token')

    this.setState({
      selectedStore: JSON.parse(user)['store_id']
    })

    axios.get(`${process.env.PUBLIC_URL}/api/getStoreStats?id=` + JSON.parse(user)['store_id'])
    .then((result)=>{
      this.setState({
        storeStatus: result.data[0]
      })
    })
    
    axios.get(`${process.env.PUBLIC_URL}/api/allOrders?id=` + JSON.parse(user)['store_id'])
    .then((result)=>{
      
      let avg_est_profit = 0
      let todays_orders = 0

      result.data.map((order)=>{
        let today = new Date()
        let order_date = new Date(order.raw_json.orderDate)

        if (today.getDate() == order_date.getDate()){
          todays_orders = todays_orders + 1
          let order_profit = Math.round(((order.purchase_price*.85) - ((order.supplier_price*1.06)*(order.raw_json.orderLines.orderLine).length)) *10) / 10
          avg_est_profit = avg_est_profit + order_profit
        }

      })

      if (result.data != []){
        this.setState({
          orders: result.data,
          todaysOrders: todays_orders,
          todaysProfit: avg_est_profit
        })
      }
    })
    
    axios.get(`${process.env.PUBLIC_URL}/api/past_due?id=` + JSON.parse(user)['store_id'])
    .then((result)=>{
      this.setState({
          lateOrders: result.data,
      })
    })

    axios.get(`${process.env.PUBLIC_URL}/api/getCSV?id=` + JSON.parse(user)['store_id'])
    .then((result)=>{
      this.setState({
        bestSellers: result.data,
        totalGross: result.data[0].total_gross,
        totalItems: result.data[0].total_items,
      })
    })
  }

  changeStore(e){
    axios.get(`${process.env.PUBLIC_URL}/api/getCSV?id=` + e.target.value)
    .then((result)=>{
      this.setState({
        bestSellers: result.data
      })
    })

    this.setState({
      selectedStore: e.target.value
    })
  }

  render(){

    var incomeOptions = {
        maintainAspectRatio: false,
        legend: {
            display: false,
        },
        scales: {
            xAxes: [{
                gridLines: {
                    color: "rgba(0, 0, 0, 0)",
                },
                display: true
            }]
        },
        plugins: {
            datalabels: {
                display: false,
            }
        }
    }


    return (
      <Fragment>
         <Breadcrumb  parent = "Dashboard"   title = "Ecommerce"  />
         <div className="container-fluid">
            <div className="row">
              <div className="col-xl-7 xl-100">
                <div className="row">
                  <div className="col-md-12 ecommerce-slider" >
                  <Slider {...this.state.settings}>
                  <div className="item">
                      <div className="card">
                        <div className="card-body ecommerce-icons text-center">
                          <DollarSign />
                          <div><span>{TotalEarning}</span></div>
                          <h4 className="font-primary mb-0">
                          <CountUp className="counter" end={this.state.revenue} /></h4>
                        </div>
                      </div>
                    </div>
                    <div className="item">
                      <div className="card">
                        <div className="card-body ecommerce-icons text-center">
                            <MapPin />
                          <div><span>Total Products</span></div>
                          <h4 className="font-primary mb-0">
                          <CountUp className="counter" end={this.state.totalItems} /></h4>
                        </div>
                      </div>
                    </div>
                    <div className="item">
                      <div className="card">
                        <div className="card-body ecommerce-icons text-center">
                          <ShoppingCart />
                          <div><span>Total Gross Sales</span></div>
                          <h4 className="font-primary mb-0">
                            <CountUp className="counter" end={this.state.totalGross} />
                          </h4>
                        </div>
                      </div>
                    </div>
                    <div className="item">
                      <div className="card">
                        <div className="card-body ecommerce-icons text-center">
                          <DollarSign />
                          <div><span>Avg Profit / Order</span></div>
                          <h4 className="font-primary mb-0">
                          { this.state.todaysProfit == 0 ? <CountUp className="counter" end={0} /> : <CountUp className="counter" end={this.state.todaysProfit/this.state.todaysOrders} />}
                          </h4>
                        </div>
                      </div>
                    </div>
                    <div className="item">
                      <div className="card">
                        <div className="card-body ecommerce-icons text-center">
                            <MapPin />
                          <div><span>Todays Orders</span></div>
                          <h4 className="font-primary mb-0">
                          <CountUp className="counter" end={this.state.todaysOrders} /></h4>
                        </div>
                      </div>
                    </div>
                  </Slider>
                  </div>
                  

                  <div className="col-md-12">
                  <div className="card">
                    <div className="card-header">
                      <h5>TOP CATEGORIES</h5>
                    </div>
                    <div className="card-body">
                          <div className="table-responsive shopping-table text-center">
                            <table className="table table-bordernone">
                              
                              <thead>
                                <tr>
                                  <th scope="col">{"Owner"}</th>
                                  <th scope="col">{"Category"}</th>
                                  <th scope="col">{"Total Earned"}</th>
                                  <th scope="col">{"Quantity"}</th>
                                  {/* <th scope="col">{"Status"}</th>
                                  <th scope="col">{"Amount"}</th>
                                  <th scope="col">{"Delete"}</th> */}
                                </tr>
                              </thead>
                              <tbody>
                                  {this.state.bestSellers.map((store)=>{
                                    return store['products'].splice(0,3).map((winners)=>{
                                      return <tr>
                                        <td>{store['name']}</td>
                                        <td>{winners['Category']}</td>
                                        <td>${Math.round(parseFloat(winners['GMV-Commission']))}</td>
                                        <td>{winners['Total Units Sold']}</td>
                                      </tr>
                                    })
                                  })}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      </div>
                      {/* <div className="card-header">
                        <h5>{TotalSale}</h5>
                      </div>
                      <div className="card-body charts-box">
                        <div className="flot-chart-container">
                          <div className="flot-chart-placeholder" id="graph123">
                            <Line data={saleData} options={saleOptions} />
                          </div>
                        </div>
                    </div> */}
                  </div>
                </div>
              </div>
              <div className="col-xl-5 xl-100">
                <div className="card">
                  <div className="card-header">
                    <h5>LATEST ORDERS</h5>
                  </div>
                  <div className="card-body">
                    <div className="table-responsive sellers">
                      <table className="table table-bordernone">
                        <thead>
                          <tr>
                            <th scope="col">Name</th>
                            <th scope="col">Sales Price</th>
                            <th scope="col">Actual Cost</th>
                            <th scope="col">Profit</th>
                          </tr>
                        </thead>
                        <tbody>
                          {this.state.orders.length >= 1 ? 
                            this.state.orders.slice(0,6).map((order)=>{
                              return <tr>
                                <td>
                                  <div className="d-inline-block align-middle">
                                    {/* <img className="img-radius img-30 align-top m-r-15 rounded-circle" src={six} alt="" /> */}
                                    <div className="d-inline-block">
                                      {/* <p>{order.name}</p> */}
                                      <p style={{fontSize:'12px', margin:'0px'}}>{order.raw_json.shippingInfo.postalAddress.name}</p>
                                    </div>
                                  </div>
                                </td>
                                <td>
                                  <p>${Math.round(order.purchase_price * 10) / 10}</p>
                                </td>
                                <td>
                                  <p>${Math.round(order.supplier_price * 10) / 10}</p>
                                </td>
                                <td>
                                  { order.profit >= 0 ?
                                  <p style={{color:'#5ad179'}}>${Math.round(((order.purchase_price*.85) - ((order.supplier_price*1.06)*(order.raw_json.orderLines.orderLine).length)) *10) / 10}</p>
                                  : <p>${Math.round(order.profit * 10) / 10}</p> }
                                </td>
                              </tr>
                            })
                          : <div>
                          </div> }
                          
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              </div>
              <div className="col-xl-3 xl-50 col-sm-6">
                <div className="card">
                  <div className="card-body">
                    <div className="number-widgets">
                      <div className="media">
                        <div className="media-body align-self-center">
                          <h6 className="mb-0">OVERALL HEALTH</h6>
                        </div>
                        <div className="radial-bar radial-bar-95 radial-bar-primary" data-label={Math.round(this.state.storeStatus.overall_score)}></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="col-xl-3 xl-50 col-sm-6">
                <div className="card">
                  <div className="card-body">
                    <div className="number-widgets">
                      <div className="media">
                        <div className="media-body align-self-center">
                          <h6 className="mb-0">Ratings</h6>
                        </div>
                        <div className="radial-bar radial-bar-75 radial-bar-primary" data-label={Math.round(this.state.storeStatus.review_score)}></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="col-xl-3 xl-50 col-sm-6">
                <div className="card">
                  <div className="card-body">
                    <div className="number-widgets">
                      <div className="media">
                        <div className="media-body align-self-center">
                          <h6 className="mb-0">Pricing</h6>
                        </div>
                        <div className="radial-bar radial-bar-90 radial-bar-primary" data-label={Math.round(this.state.storeStatus.pricing_quality)}></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="col-xl-3 xl-50 col-sm-6">
                <div className="card">
                  <div className="card-body">
                    <div className="number-widgets">
                      <div className="media">
                        <div className="media-body align-self-center">
                          <h6 className="mb-0">Products</h6>
                        </div>
                        <div className="radial-bar radial-bar-80 radial-bar-primary" data-label={this.state.storeStatus.listing_quality}></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              { (localStorage.getItem('role') == 'admin' || localStorage.getItem('role') == 'assistant') ? <div>
                  <div className="col-md-6">
                    <div className="card">
                      <div className="card-header">
                        <h5>DAILY ORDERS BY STORE</h5>
                      </div>
                      <div className="card-body chart-block ecommerce-income">
                          <Line data={this.state.graphData} options={incomeOptions}  />
                      </div>
                    </div>
                  </div>
                  <div className="col-md-6">
                    <div className="card">
                      <div className="card-header">
                        <h5>{TotalProfit}</h5>
                      </div>
                      <div className="card-body chart-block ecommerce-income">
                      <Line data={profitData} options={profitOptions}  />
                      </div>
                    </div>
                  </div>
                  <div className="col-xl-4 xl-50 col-md-6">
                    <div className="card">
                      <div className="card-header">
                        <h5>{JSON.parse(localStorage.getItem('token'))['name']}</h5>
                      </div>
                      <div className="card-body height-equal">

                      {localStorage.getItem('role') == 'user' ?
                              <div>
                                <div className="progress-block">
                                  <div className="progress-title"><span style={{textDecorationStyle: 'solid'}}>Overall</span><span className="pull-right">{Math.round(this.state.storeStatus.overall_score)}%</span></div>
                                  <div className="progress" style={{ height: "3px", textDecorationStyle: 'solid',  }}>
                                    <div className="progress-bar bg-danger" role="progressbar" style={{ twidth: this.state.storeStatus.overall_score + '%' }} aria-valuenow={this.state.storeStatus.overall_score} aria-valuemin="0" aria-valuemax="100"></div>
                                  </div>
                                </div>
                                <div className="progress-block">
                                  <div className="progress-title"><span style={{textDecorationStyle: 'solid'}}>Reviews</span><span className="pull-right">{Math.round(this.state.storeStatus.review_score)}%</span></div>
                                  <div className="progress" style={{ height: "3px", textDecorationStyle: 'solid',  }}>
                                  <div className="progress-bar bg-danger" role="progressbar" style={{ twidth: this.state.storeStatus.review_score + '%' }} aria-valuenow={this.state.storeStatus.review_score} aria-valuemin="0" aria-valuemax="100"></div>
                                  </div>
                                </div>
                                <div className="progress-block">
                                  <div className="progress-title"><span style={{textDecorationStyle: 'solid'}}>Listing Quality</span><span className="pull-right">{Math.round(this.state.storeStatus.listing_quality)}%</span></div>
                                  <div className="progress" style={{ height: "3px", textDecorationStyle: 'solid',  }}>
                                  <div className="progress-bar bg-danger" role="progressbar" style={{ twidth: this.state.storeStatus.listing_quality + '%' }} aria-valuenow={this.state.storeStatus.listing_quality} aria-valuemin="0" aria-valuemax="100"></div>
                                  </div>
                                </div>
                                <div className="progress-block">
                                  <div className="progress-title"><span style={{textDecorationStyle: 'solid'}}>Pricing</span><span className="pull-right">{Math.round(this.state.storeStatus.pricing_quality)}%</span></div>
                                  <div className="progress" style={{ height: "3px", textDecorationStyle: 'solid',  }}>
                                  <div className="progress-bar bg-danger" role="progressbar" style={{ twidth: this.state.storeStatus.pricing_quality + '%' }} aria-valuenow={this.state.storeStatus.pricing_quality} aria-valuemin="0" aria-valuemax="100"></div>
                                  </div>
                                </div>
                              </div> : null }
                      </div>
                    </div>
                  </div>
                  <div className="col-xl-4 xl-50 col-md-6">
                    <div className="card">
                      <div className="card-header">
                        <h5>Late Orders</h5>
                      
                      </div>
                      <div className="card-body height-equal log-content">
                        {this.state.lateOrders.map((order)=>{
                          return <div className="logs-element">
                            <div className="circle-double-odd"></div><span>{order['name']}</span><span className="pull-right">{order['purchaseOrderId']}</span>
                          </div>
                        })}
                      </div>
                    </div>
                  </div>
                  <div className="col-xl-4 xl-100">
                    <div className="card">
                      <div className="card-header">
                        <h5>{"statics"}</h5>
                      </div>
                      <div className="card-body updating-chart height-equal">
                        <div className="upadates text-center">
                          <h2 className="font-primary">
                            <DollarSign />
                            <span> <CountUp className="counter" end={89.65} />{"89.68"} </span>
                            <ArrowUp />
                          </h2>
                          <p>{"Week2 +"}<span><CountUp className="counter" end={15.44} />{"15.44"}</span></p>
                        </div>
                        <div className="flot-chart-container">
                          <div className="flot-chart-placeholder" id="updating-data-morris-chart">
                              <Line data={staticData} options={staticOptions}  />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="col-xl-8 xl-50">
                    <div className="card">
                      <div className="card-header" style={{display:'flex', flexDirection:'row', justifyContent:'space-between'}}>
                        <h5>Best Sellers</h5>
                        <select value={this.state.selectedStore} onChange={(e)=>{this.changeStore(e)}}>

                          <option value="1">Grapefruit</option>
                          <option value="2">Lime</option>
                          <option value="3">Coconut</option>
                          <option value="4">Mango</option>
                        </select>
                      </div>

                    </div>
                  </div>
                  <div className="col-xl-4 xl-50">
                    <div className="card">
                      <div className="card-header">
                        <h5>{Review}</h5>
                      </div>
                      <div className="card-body">
                        <div className="text-center knob-block">
                          <div className="knob" id="profit">
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div> : null}
            </div>
          </div>
      </Fragment>
    )
  }
}