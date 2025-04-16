package com.example.stock.service;

import org.springframework.stereotype.Service;

import com.example.stock.dto.StockResponse;

/**
 * 股票数据服务接口
 */
@Service
public interface StockService {

  /**
   * 获取所有股票数据
   * 
   * @param tsCode    股票代码
   * @param tradeDate 交易日期
   * @param pageNum   页码
   * @return 股票数据响应
   */
  StockResponse getAllData(String tsCode, String tradeDate, Integer pageNum);

  /**
   * 获取涨停股票数据
   * 
   * @param tsCode    股票代码
   * @param tradeDate 交易日期
   * @param pageNum   页码
   * @return 股票数据响应
   */
  StockResponse getLimitUpData(String tsCode, String tradeDate, Integer pageNum);

  /**
   * 获取跌停股票数据
   * 
   * @param tsCode    股票代码
   * @param tradeDate 交易日期
   * @param pageNum   页码
   * @return 股票数据响应
   */
  StockResponse getLimitDownData(String tsCode, String tradeDate, Integer pageNum);

  /**
   * 获取半年线股票数据
   * 
   * @param tsCode    股票代码
   * @param tradeDate 交易日期
   * @param pageNum   页码
   * @return 股票数据响应
   */
  StockResponse getHalfYearLineData(String tsCode, String tradeDate, Integer pageNum);

  /**
   * 获取年线股票数据
   * 
   * @param tsCode    股票代码
   * @param tradeDate 交易日期
   * @param pageNum   页码
   * @return 股票数据响应
   */
  StockResponse getYearLineData(String tsCode, String tradeDate, Integer pageNum);
}