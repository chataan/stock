//
//  ViewController.swift
//  prophet
//
//  Created by 준영 on 12/24/19.
//  Copyright © 2019 준영. All rights reserved.
//

import UIKit

class ViewController: UIViewController {

    @IBOutlet weak var StockNameLabel: UILabel!
    @IBOutlet weak var StatusLabel: UILabel!
    @IBOutlet weak var SearchBar: UITextField!
    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view.
    }
   
    @IBAction func search(_ sender: UIButton) {
        // request stock data from finance.yahoo.com
        // read stock data, create line graph
        // make predictions of the stock price using the pre-trained models loaded in the application
        if SearchBar.text != "" {
            if (SearchBar.text == "reset") || (SearchBar.text == "Reset") {
                StatusLabel.text = "Get started by searching a stock!"
                StockNameLabel.text = ""
                SearchBar.text = ""
            }
            else {
                StockNameLabel.text = SearchBar.text
                SearchBar.text = ""
                StatusLabel.text = "Stock data acquired from finanace.yahoo.com"
            }
        } else {}
    }
}
