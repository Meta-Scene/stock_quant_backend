package com.example.stock.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDate;

@Data
@TableName("public.all_stocks_days")
public class StockData {
  @TableId(type = IdType.AUTO)
  private Long id;
  private String tsCode;
  private LocalDate tradeDate;
  private BigDecimal open;
  private BigDecimal high;
  private BigDecimal low;
  private BigDecimal close;
  private BigDecimal preClose;
  private BigDecimal pctChg;
  private BigDecimal vol;
  private BigDecimal amount;
  private BigDecimal turnoverRate;
  private BigDecimal ma5; // 5日均线
  private BigDecimal ma10; // 10日均线
  private BigDecimal ma120; // 半年线
  private BigDecimal ma250; // 年线
}