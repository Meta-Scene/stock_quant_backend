package com.example.stock.service.impl;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.example.stock.dto.StockResponse;
import com.example.stock.entity.StockData;
import com.example.stock.mapper.StockDataMapper;
import com.example.stock.service.StockService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.AbstractMap.SimpleImmutableEntry;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
public class StockServiceImpl implements StockService {

  @Autowired
  private StockDataMapper stockDataMapper;

  @Value("${stock.page.size}")
  private int pageSize;

  private static final DateTimeFormatter DATE_FORMATTER = DateTimeFormatter.ofPattern("yyyyMMdd");

  @Override
  public StockResponse getAllData(String tsCode, String tradeDate, Integer pageNum) {
    // 解析传入的日期
    LocalDate targetDate = parseDate(tradeDate);
    if (targetDate == null) {
      targetDate = stockDataMapper.findMaxDate();
    }

    int offset = (pageNum != null ? pageNum - 1 : 0) * pageSize;

    // 严格使用指定日期查询，SQL会自动计算前后20个交易日的范围
    List<StockData> stockList = stockDataMapper.findByDateRange(
        tsCode,
        targetDate,
        null, // 不需要显式传递endDate，SQL会自动计算
        pageSize,
        offset);

    Long totalCount = stockDataMapper.countStocks(tsCode, targetDate, null, null, null);

    // 如果没有数据，返回一个空响应
    if (stockList.isEmpty()) {
      return buildEmptyResponse(targetDate, pageNum, tradeDate);
    }

    // 从查询结果中获取实际的日期范围
    LocalDate startDate = stockList.stream()
        .map(StockData::getTradeDate)
        .min(LocalDate::compareTo)
        .orElse(targetDate);
    LocalDate endDate = stockList.stream()
        .map(StockData::getTradeDate)
        .max(LocalDate::compareTo)
        .orElse(targetDate);

    return buildResponse(stockList, startDate, endDate, totalCount.intValue(), pageNum, tradeDate);
  }

  @Override
  public StockResponse getLimitUpData(String tsCode, String tradeDate, Integer pageNum) {
    // 解析传入的日期
    LocalDate targetDate = parseDate(tradeDate);
    if (targetDate == null) {
      targetDate = stockDataMapper.findMaxDate();
    }

    int offset = (pageNum != null ? pageNum - 1 : 0) * pageSize;

    // 严格使用指定日期筛选涨停股票
    List<StockData> stockList = stockDataMapper.findLimitUp(
        tsCode,
        targetDate,
        null,
        pageSize,
        offset);

    Long totalCount = stockDataMapper.countStocks(tsCode, targetDate, null, true, null);

    // 如果没有数据，返回一个空响应
    if (stockList.isEmpty()) {
      return buildEmptyResponse(targetDate, pageNum, tradeDate);
    }

    // 显示使用日期范围的开始和结束日期（如果有数据）
    LocalDate startDate = stockList.stream()
        .map(StockData::getTradeDate)
        .min(LocalDate::compareTo)
        .orElse(targetDate);
    LocalDate endDate = stockList.stream()
        .map(StockData::getTradeDate)
        .max(LocalDate::compareTo)
        .orElse(targetDate);

    return buildLimitResponse(stockList, startDate, endDate, totalCount.intValue(), pageNum, tradeDate);
  }

  @Override
  public StockResponse getLimitDownData(String tsCode, String tradeDate, Integer pageNum) {
    // 解析传入的日期
    LocalDate targetDate = parseDate(tradeDate);
    if (targetDate == null) {
      targetDate = stockDataMapper.findMaxDate();
    }

    int offset = (pageNum != null ? pageNum - 1 : 0) * pageSize;

    // 严格使用指定日期筛选跌停股票
    List<StockData> stockList = stockDataMapper.findLimitDown(
        tsCode,
        targetDate,
        null,
        pageSize,
        offset);

    Long totalCount = stockDataMapper.countStocks(tsCode, targetDate, null, null, true);

    // 如果没有数据，返回一个空响应
    if (stockList.isEmpty()) {
      return buildEmptyResponse(targetDate, pageNum, tradeDate);
    }

    // 显示使用日期范围的开始和结束日期（如果有数据）
    LocalDate startDate = stockList.stream()
        .map(StockData::getTradeDate)
        .min(LocalDate::compareTo)
        .orElse(targetDate);
    LocalDate endDate = stockList.stream()
        .map(StockData::getTradeDate)
        .max(LocalDate::compareTo)
        .orElse(targetDate);

    return buildLimitResponse(stockList, startDate, endDate, totalCount.intValue(), pageNum, tradeDate);
  }

  @Override
  public StockResponse getHalfYearLineData(String tsCode, String tradeDate, Integer pageNum) {
    // 解析传入的日期
    LocalDate targetDate = parseDate(tradeDate);
    if (targetDate == null) {
      targetDate = stockDataMapper.findMaxDate();
    }

    int offset = (pageNum != null ? pageNum - 1 : 0) * pageSize;

    // 查询半年线数据
    List<StockData> stockList = stockDataMapper.findHalfYearLine(
        tsCode,
        targetDate,
        pageSize,
        offset);

    Long totalCount = stockDataMapper.countHalfYearLineStocks(tsCode, targetDate);

    // 如果没有数据，返回一个空响应
    if (stockList.isEmpty()) {
      return buildEmptyResponse(targetDate, pageNum, tradeDate);
    }

    // 从查询结果中获取实际的日期范围
    LocalDate startDate = stockList.stream()
        .map(StockData::getTradeDate)
        .min(LocalDate::compareTo)
        .orElse(targetDate);
    LocalDate endDate = stockList.stream()
        .map(StockData::getTradeDate)
        .max(LocalDate::compareTo)
        .orElse(targetDate);

    return buildMaResponse(stockList, startDate, endDate, totalCount.intValue(), pageNum, tradeDate, "ma120");
  }

  @Override
  public StockResponse getYearLineData(String tsCode, String tradeDate, Integer pageNum) {
    // 解析传入的日期
    LocalDate targetDate = parseDate(tradeDate);
    if (targetDate == null) {
      targetDate = stockDataMapper.findMaxDate();
    }

    int offset = (pageNum != null ? pageNum - 1 : 0) * pageSize;

    // 查询年线数据
    List<StockData> stockList = stockDataMapper.findYearLine(
        tsCode,
        targetDate,
        pageSize,
        offset);

    Long totalCount = stockDataMapper.countYearLineStocks(tsCode, targetDate);

    // 如果没有数据，返回一个空响应
    if (stockList.isEmpty()) {
      return buildEmptyResponse(targetDate, pageNum, tradeDate);
    }

    // 从查询结果中获取实际的日期范围
    LocalDate startDate = stockList.stream()
        .map(StockData::getTradeDate)
        .min(LocalDate::compareTo)
        .orElse(targetDate);
    LocalDate endDate = stockList.stream()
        .map(StockData::getTradeDate)
        .max(LocalDate::compareTo)
        .orElse(targetDate);

    return buildMaResponse(stockList, startDate, endDate, totalCount.intValue(), pageNum, tradeDate, "ma250");
  }

  /**
   * 获取日期范围
   *
   * @param tradeDate 交易日期
   * @return 日期范围
   */
  private SimpleImmutableEntry<LocalDate, LocalDate> getDateRange(LocalDate tradeDate) {
    LocalDate targetDate = tradeDate;
    if (targetDate == null) {
      targetDate = LocalDate.now();
    }

    // 确保目标日期不超过数据库中的最大日期
    LocalDate maxDate = stockDataMapper.findMaxDate();
    if (targetDate.isAfter(maxDate)) {
      targetDate = maxDate;
    }

    // 获取目标日期前后20个交易日的日期范围
    LocalDate startDate = stockDataMapper.findPreviousNthTradeDate(targetDate, 20);
    if (startDate == null) {
      startDate = stockDataMapper.findMinDate(); // 如果没有足够的交易日，则使用最早日期
    }

    LocalDate endDate = stockDataMapper.findNextNthTradeDate(targetDate, 20);
    if (endDate == null) {
      endDate = maxDate; // 如果没有足够的交易日，则使用最晚日期
    }

    return new SimpleImmutableEntry<>(startDate, endDate);
  }

  /**
   * 解析日期字符串为LocalDate
   * 
   * @param dateStr 日期字符串
   * @return LocalDate对象，如果字符串为空则返回null
   */
  private LocalDate parseDate(String dateStr) {
    if (dateStr == null || dateStr.isEmpty()) {
      return null;
    }
    return LocalDate.parse(dateStr);
  }

  /**
   * 构建响应对象
   */
  private StockResponse buildResponse(List<StockData> stockDataList,
      LocalDate startDate, LocalDate endDate,
      int totalStocks, Integer pageNum, String tradeDateStr) {
    StockResponse response = new StockResponse();

    // 设置列名
    response.setColumn_names(Arrays.asList(
        "ts_code", "trade_date", "open", "high",
        "low", "close", "pre_close", "pct_chg", "vol", "amount",
        "turnover_rate", "ma5", "ma10", "ma120", "ma250"));

    // 设置查询日期
    response.setDate(tradeDateStr != null ? tradeDateStr : LocalDate.now().toString());

    // 设置分页信息
    int page = pageNum != null ? pageNum : 1;
    response.setPage(page);

    // 根据tradeDateStr获取基准日期
    LocalDate baseDate = tradeDateStr != null ? parseDate(tradeDateStr) : LocalDate.now();

    // 获取具有最大涨跌幅的股票编码及其涨跌幅值
    Map<String, Double> maxPctChgByStockOnDate = new HashMap<>();

    for (StockData stock : stockDataList) {
      String tsCode = stock.getTsCode();
      LocalDate stockDate = stock.getTradeDate();

      // 只考虑基准日期当天或最近的一天的涨跌幅
      if (!maxPctChgByStockOnDate.containsKey(tsCode) ||
          Math.abs(stockDate.toEpochDay() - baseDate.toEpochDay()) < Math
              .abs(getClosestDateForStock(stockDataList, tsCode, baseDate).toEpochDay() - baseDate.toEpochDay())) {
        maxPctChgByStockOnDate.put(tsCode, stock.getPctChg().doubleValue());
      }
    }

    // 将股票数据按照股票代码分组
    Map<String, List<StockResponse.StockData>> groupedDataByStock = stockDataList.stream()
        .map(this::convertToDto)
        .collect(Collectors.groupingBy(StockResponse.StockData::getTsCode));

    // 按当天涨跌幅对股票代码进行排序
    List<String> sortedStockCodes = new ArrayList<>(groupedDataByStock.keySet());
    sortedStockCodes.sort((tsCode1, tsCode2) -> Double.compare(maxPctChgByStockOnDate.getOrDefault(tsCode2, 0.0),
        maxPctChgByStockOnDate.getOrDefault(tsCode1, 0.0)));

    // 转换为grid_data格式：List<List<List<Object>>>
    List<List<List<Object>>> gridData = new ArrayList<>();

    for (String tsCode : sortedStockCodes) {
      List<List<Object>> stockDataArray = new ArrayList<>();

      // 对同一只股票的数据按照日期升序排序
      List<StockResponse.StockData> sortedData = groupedDataByStock.get(tsCode).stream()
          .sorted(Comparator.comparing(StockResponse.StockData::getTradeDate))
          .collect(Collectors.toList());

      // 将每个股票的数据转换为Object[]并添加到stockDataArray
      for (StockResponse.StockData data : sortedData) {
        stockDataArray.add(Arrays.asList(data.toObjectArray()));
      }

      gridData.add(stockDataArray);
    }

    // 设置响应数据
    response.setGrid_data(gridData);
    response.setStock_count(totalStocks);

    return response;
  }

  /**
   * 获取某只股票在给定日期最近的交易日
   */
  private LocalDate getClosestDateForStock(List<StockData> stockDataList, String tsCode, LocalDate targetDate) {
    return stockDataList.stream()
        .filter(stock -> stock.getTsCode().equals(tsCode))
        .map(StockData::getTradeDate)
        .min(Comparator.comparing(date -> Math.abs(date.toEpochDay() - targetDate.toEpochDay())))
        .orElse(targetDate);
  }

  /**
   * 构建涨停/跌停响应对象
   */
  private StockResponse buildLimitResponse(List<StockData> stockDataList,
      LocalDate startDate, LocalDate endDate,
      int totalStocks, Integer pageNum, String tradeDateStr) {
    StockResponse response = new StockResponse();

    // 设置列名
    response.setColumn_names(Arrays.asList(
        "ts_code", "trade_date", "open", "high",
        "low", "close", "pre_close", "pct_chg", "vol", "amount",
        "turnover_rate", "ma5", "ma10", "ma120", "ma250"));

    // 设置查询日期
    response.setDate(tradeDateStr != null ? tradeDateStr : LocalDate.now().toString());

    // 设置分页信息
    int page = pageNum != null ? pageNum : 1;
    response.setPage(page);

    // 根据tradeDateStr获取基准日期
    LocalDate baseDate = tradeDateStr != null ? parseDate(tradeDateStr) : stockDataMapper.findMaxDate();

    // 将股票数据按照股票代码分组
    Map<String, List<StockResponse.StockData>> groupedDataByStock = stockDataList.stream()
        .map(this::convertToDto)
        .collect(Collectors.groupingBy(StockResponse.StockData::getTsCode));

    // 获取特定日期的数据用于排序（股票代码已在SQL中按涨跌幅排序）
    List<String> sortedStockCodes = new ArrayList<>(groupedDataByStock.keySet());

    // 转换为grid_data格式：List<List<List<Object>>>
    List<List<List<Object>>> gridData = new ArrayList<>();

    for (String tsCode : sortedStockCodes) {
      List<List<Object>> stockDataArray = new ArrayList<>();

      // 对同一只股票的数据按照日期升序排序
      List<StockResponse.StockData> sortedData = groupedDataByStock.get(tsCode).stream()
          .sorted(Comparator.comparing(StockResponse.StockData::getTradeDate))
          .collect(Collectors.toList());

      // 将每个股票的数据转换为Object[]并添加到stockDataArray
      for (StockResponse.StockData data : sortedData) {
        stockDataArray.add(Arrays.asList(data.toObjectArray()));
      }

      gridData.add(stockDataArray);
    }

    // 设置响应数据
    response.setGrid_data(gridData);
    response.setStock_count(totalStocks);

    return response;
  }

  /**
   * 构建均线响应对象
   */
  private StockResponse buildMaResponse(List<StockData> stockDataList,
      LocalDate startDate, LocalDate endDate,
      int totalStocks, Integer pageNum, String tradeDateStr, String maType) {
    StockResponse response = new StockResponse();

    // 设置列名
    response.setColumn_names(Arrays.asList(
        "ts_code", "trade_date", "open", "high",
        "low", "close", "pre_close", "pct_chg", "vol", "amount",
        "turnover_rate", "ma5", "ma10", "ma120", "ma250"));

    // 设置查询日期
    response.setDate(tradeDateStr != null ? tradeDateStr : LocalDate.now().toString());

    // 设置分页信息
    int page = pageNum != null ? pageNum : 1;
    response.setPage(page);

    // 将股票数据按照股票代码分组
    Map<String, List<StockResponse.StockData>> groupedDataByStock = stockDataList.stream()
        .map(this::convertToDto)
        .collect(Collectors.groupingBy(StockResponse.StockData::getTsCode));

    // 转换为grid_data格式：List<List<List<Object>>>
    List<List<List<Object>>> gridData = new ArrayList<>();

    for (String tsCode : groupedDataByStock.keySet()) {
      List<List<Object>> stockDataArray = new ArrayList<>();

      // 对同一只股票的数据按照日期升序排序
      List<StockResponse.StockData> sortedData = groupedDataByStock.get(tsCode).stream()
          .sorted(Comparator.comparing(StockResponse.StockData::getTradeDate))
          .collect(Collectors.toList());

      // 将每个股票的数据转换为Object[]并添加到stockDataArray
      for (StockResponse.StockData data : sortedData) {
        stockDataArray.add(Arrays.asList(data.toObjectArray()));
      }

      gridData.add(stockDataArray);
    }

    // 设置响应数据
    response.setGrid_data(gridData);
    response.setStock_count(totalStocks);

    return response;
  }

  /**
   * 转换为DTO对象
   */
  private StockResponse.StockData convertToDto(StockData entity) {
    StockResponse.StockData dto = new StockResponse.StockData();
    dto.setTsCode(entity.getTsCode());
    dto.setTradeDate(entity.getTradeDate());
    dto.setOpen(entity.getOpen());
    dto.setHigh(entity.getHigh());
    dto.setLow(entity.getLow());
    dto.setClose(entity.getClose());
    dto.setPreClose(entity.getPreClose());
    dto.setPctChg(entity.getPctChg());
    dto.setVol(entity.getVol());
    dto.setAmount(entity.getAmount());
    dto.setTurnoverRate(entity.getTurnoverRate());
    dto.setMa5(entity.getMa5());
    dto.setMa10(entity.getMa10());
    dto.setMa120(entity.getMa120());
    dto.setMa250(entity.getMa250());
    return dto;
  }

  /**
   * 构建空响应对象
   */
  private StockResponse buildEmptyResponse(LocalDate targetDate, Integer pageNum, String tradeDateStr) {
    StockResponse response = new StockResponse();

    // 设置列名
    response.setColumn_names(Arrays.asList(
        "ts_code", "trade_date", "open", "high",
        "low", "close", "pre_close", "pct_chg", "vol", "amount",
        "turnover_rate", "ma5", "ma10", "ma120", "ma250"));

    // 设置查询日期
    response.setDate(tradeDateStr != null ? tradeDateStr : targetDate.toString());

    // 设置分页信息
    int page = pageNum != null ? pageNum : 1;
    response.setPage(page);

    // 设置空数据
    response.setGrid_data(new ArrayList<>());
    response.setStock_count(0);

    return response;
  }
}