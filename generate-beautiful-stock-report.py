#!/usr/bin/env python3
"""
生成漂亮的股票分析报告（竖版高清模板）
使用之前保存的 report-template-final.html 模板
"""

import os
import sys
import base64
import datetime
from playwright.sync_api import sync_playwright
import asyncio

# 添加路径
sys.path.insert(0, '/root/.openclaw/workspace/skills/stock-analysis-lianghua-integrated')

from stock_data_query import StockDataQuery
from quant_analysis import QuantitativeAnalyzer

async def get_analysis_data(symbol):
    """获取分析数据"""
    query = StockDataQuery()
    analyzer = QuantitativeAnalyzer(query)
    result = await analyzer.analyze_stock(symbol, '3mo')
    return result

def generate_report_with_real_data(symbol, stock_name, analysis_result, chart_path, output_path):
    """用真实数据生成报告"""
    
    # 读取图表
    with open(chart_path, "rb") as f:
        chart_base64 = base64.b64encode(f.read()).decode()
    
    # 读取模板
    template_path = "/root/.openclaw/workspace/report-template-final.html"
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # 提取真实数据
    realtime_price = analysis_result.get('realtime_price', {})
    composite_score = analysis_result.get('composite_score', 0)
    signals = analysis_result.get('signals', {})
    chip_data = analysis_result.get('chip_data', {})
    fund_flow = analysis_result.get('fund_flow_data', {})
    related_news = analysis_result.get('related_news', [])
    factor_scores = analysis_result.get('factor_scores', {})
    support_resistance = analysis_result.get('support_resistance', {})
    
    # 替换基本信息
    html_content = html_content.replace("__STOCK_NAME__", stock_name)
    html_content = html_content.replace("__STOCK_CODE__", symbol)
    html_content = html_content.replace("__CHART_BASE64__", chart_base64)
    
    # 时间戳
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html_content = html_content.replace("__TIMESTAMP__", timestamp)
    
    # 价格数据
    price = realtime_price.get('price', 0)
    change = realtime_price.get('change', 0)
    change_percent = realtime_price.get('change_percent', 0)
    currency = realtime_price.get('currency', 'HKD')
    action = signals.get('action', 'hold')
    
    html_content = html_content.replace("__PRICE__", f"{price:.2f} {currency}")
    
    change_str = f"{change_percent:+.2f}%"
    html_content = html_content.replace("__CHANGE__", change_str)
    
    html_content = html_content.replace("__SCORE__", f"{composite_score:.1f}")
    
    action_map = {
        'strong_buy': '强烈买入',
        'buy': '买入',
        'hold': '观望',
        'sell': '卖出'
    }
    html_content = html_content.replace("__SIGNAL__", action_map.get(action, action.upper()))
    
    # CSS类
    price_class = ""
    change_class = "negative" if change < 0 else "" if change == 0 else ""
    score_class = "warning" if 40 <= composite_score <= 60 else "negative" if composite_score < 40 else ""
    signal_class = "neutral" if action == 'hold' else "negative" if action == 'sell' else ""
    
    html_content = html_content.replace("__PRICE_CLASS__", price_class)
    html_content = html_content.replace("__CHANGE_CLASS__", change_class)
    html_content = html_content.replace("__SCORE_CLASS__", score_class)
    html_content = html_content.replace("__SIGNAL_CLASS__", signal_class)
    
    # 分析要点
    analysis_items = ""
    
    # 实时行情
    volume = realtime_price.get('volume', 0)
    turnover = realtime_price.get('turnover', 0)
    analysis_items += f"""
    <div class="analysis-item">
        <div class="analysis-header">
            <span class="analysis-icon">💹</span>
            <div class="analysis-title">实时行情</div>
        </div>
        <div class="analysis-content">价格 {price:.2f} {currency}，{change_str}，成交 {volume/10000000:.1f}亿股 / {turnover/100000000:.2f}亿{currency}</div>
    </div>
    """
    
    # 量化评分
    analysis_items += f"""
    <div class="analysis-item">
        <div class="analysis-header">
            <span class="analysis-icon">⭐</span>
            <div class="analysis-title">量化评分</div>
        </div>
        <div class="analysis-content">综合评分 {composite_score:.1f}/100，信号：{action_map.get(action, action.upper())}，置信度 {signals.get('confidence', 0):.0f}%</div>
    </div>
    """
    
    # 因子分析
    trend = factor_scores.get('trend', 0)
    momentum = factor_scores.get('momentum', 0)
    volatility = factor_scores.get('volatility', 0)
    volume_factor = factor_scores.get('volume', 0)
    analysis_items += f"""
    <div class="analysis-item">
        <div class="analysis-header">
            <span class="analysis-icon">📊</span>
            <div class="analysis-title">因子分析</div>
        </div>
        <div class="analysis-content">趋势 {trend:.0f} | 动量 {momentum:.0f} | 波动 {volatility:.0f} | 成交量 {volume_factor:.0f}</div>
    </div>
    """
    
    # 筹码分布
    if chip_data:
        avg_cost = chip_data.get('avg_cost', 0)
        profit_pct = chip_data.get('profit_percent', 0)
        p90_range = chip_data.get('p90', {}).get('priceRange', '')
        analysis_items += f"""
        <div class="analysis-item">
            <div class="analysis-header">
                <span class="analysis-icon">🎲</span>
                <div class="analysis-title">筹码分布</div>
            </div>
            <div class="analysis-content">平均成本 {avg_cost:.2f}，获利比例 {profit_pct:.1f}%，90%筹码 {p90_range}</div>
        </div>
        """
    
    # 资金流向
    if fund_flow:
        if fund_flow.get('market') == 'HK':
            latest = fund_flow.get('latest', {})
            hkex_ratio = latest.get('hkex_ratio', 0)
            short_ratio = latest.get('short_ratio', 0)
            analysis_items += f"""
            <div class="analysis-item">
                <div class="analysis-header">
                    <span class="analysis-icon">💰</span>
                    <div class="analysis-title">资金流向</div>
                </div>
                <div class="analysis-content">港股通持股 {hkex_ratio:.2f}%，卖空占比 {short_ratio:.2f}%</div>
            </div>
            """
        elif fund_flow.get('market') == 'CN':
            main_fund = fund_flow.get('main_fund', {})
            if main_fund:
                net_inflow = main_fund.get('today_net_inflow', 0)
                flow_icon = "🟢" if net_inflow > 0 else "🔴"
                analysis_items += f"""
                <div class="analysis-item">
                    <div class="analysis-header">
                        <span class="analysis-icon">💰</span>
                        <div class="analysis-title">资金流向</div>
                    </div>
                    <div class="analysis-content">主力净流入 {flow_icon} {net_inflow:,.0f}</div>
                </div>
                """
    
    # 关键价位
    support = support_resistance.get('support', [])
    resistance = support_resistance.get('resistance', [])
    support_str = ', '.join([f'{x:.2f}' for x in support[:3]]) if support else '-'
    resistance_str = ', '.join([f'{x:.2f}' for x in resistance[:3]]) if resistance else '-'
    analysis_items += f"""
    <div class="analysis-item">
        <div class="analysis-header">
            <span class="analysis-icon">🎯</span>
            <div class="analysis-title">关键价位</div>
        </div>
        <div class="analysis-content">支撑位 {support_str}，阻力位 {resistance_str}</div>
    </div>
    """
    
    html_content = html_content.replace("__ANALYSIS_ITEMS__", analysis_items)
    
    # 新闻
    news_items = ""
    source_map = {0: '36氪', 1: '财联社', 2: '智通财经', 3: '腾讯财经', 4: '新浪财经'}
    for i, news in enumerate(related_news[:3]):
        title = news.get('title', '')
        snippet = news.get('summary', '') or news.get('snippet', '')
        if snippet and len(snippet) > 100:
            snippet = snippet[:100] + "..."
        source = source_map.get(i, '财经媒体')
        news_items += f"""
        <div class="news-item">
            <div class="news-header">
                <span class="news-icon">📡</span>
                <div class="news-source">{source}</div>
            </div>
            <div class="news-title">{title}</div>
            <div class="news-snippet">{snippet}</div>
        </div>
        """
    
    html_content = html_content.replace("__NEWS_ITEMS__", news_items)
    
    # 保存临时HTML
    temp_html = f"/tmp/stock-report-{symbol}-temp.html"
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    # 用 Playwright 截图 - 高清！
    print(f"📸 正在生成报告: {stock_name} ({symbol})")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={"width": 1000, "height": 2200},
            device_scale_factor=2  # 2x 高清！
        )
        page.goto(f"file://{temp_html}")
        page.wait_for_load_state("networkidle")
        page.screenshot(path=output_path, full_page=True, type="png")
        browser.close()
    
    # 清理临时文件
    try:
        os.remove(temp_html)
    except:
        pass
    
    print(f"✅ 报告已生成: {output_path}")
    return output_path

def main(symbol, stock_name, output_path=None):
    """主函数"""
    # 获取分析数据
    analysis_result = asyncio.run(get_analysis_data(symbol))
    chart_path = analysis_result.get('chart_path')
    
    if not chart_path:
        print("❌ 未生成图表，无法生成报告")
        return None
    
    if output_path is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"/tmp/stock-report-{symbol}-{timestamp}.png"
    
    return generate_report_with_real_data(symbol, stock_name, analysis_result, chart_path, output_path)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("使用方法: python3 generate-beautiful-stock-report.py <股票代码> <股票名称> [输出路径]")
        print("示例: python3 generate-beautiful-stock-report.py 1810.HK '小米集团-W'")
        sys.exit(1)
    
    symbol = sys.argv[1]
    stock_name = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else None
    
    main(symbol, stock_name, output_path)
