package com.example.stock.controller;

import com.example.stock.dto.StockResponse;
import com.example.stock.service.StockService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/stock")
@CrossOrigin(origins = "*")
public class StockController {

  // 注入StockService
  private final StockService stockService;

  // 构造函数注入StockService
  public StockController(StockService stockService) {
    this.stockService = stockService;
  }

  // 查询所有股票数据
  @GetMapping("/data")
  public StockResponse getAllData(
      @RequestParam(required = false) String tsCode,
      @RequestParam(required = false) String tradeDate,
      @RequestParam(required = false, defaultValue = "1") Integer pageNum) {
    return stockService.getAllData(tsCode, tradeDate, pageNum);
  }

  // 查询涨停股票数据
  @GetMapping("/limit-up")
  public StockResponse getLimitUpData(
      @RequestParam(required = false) String tsCode,
      @RequestParam(required = false) String tradeDate,
      @RequestParam(required = false, defaultValue = "1") Integer pageNum) {
    return stockService.getLimitUpData(tsCode, tradeDate, pageNum);
  }

  // 查询跌停股票数据
  @GetMapping("/limit-down")
  public StockResponse getLimitDownData(
      @RequestParam(required = false) String tsCode,
      @RequestParam(required = false) String tradeDate,
      @RequestParam(required = false, defaultValue = "1") Integer pageNum) {
    return stockService.getLimitDownData(tsCode, tradeDate, pageNum);
  }

  // 查询半年线股票数据
  @GetMapping("/half-year-line")
  public StockResponse getHalfYearLineData(
      @RequestParam(required = false) String tsCode,
      @RequestParam(required = false) String tradeDate,
      @RequestParam(required = false, defaultValue = "1") Integer pageNum) {
    return stockService.getHalfYearLineData(tsCode, tradeDate, pageNum);
  }

  // 查询年线股票数据
  @GetMapping("/year-line")
  public StockResponse getYearLineData(
      @RequestParam(required = false) String tsCode,
      @RequestParam(required = false) String tradeDate,
      @RequestParam(required = false, defaultValue = "1") Integer pageNum) {
    return stockService.getYearLineData(tsCode, tradeDate, pageNum);
  }
}